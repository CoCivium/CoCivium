/**
 * CoInputGap R0: deterministic, app-owned idle-interval proposal state machine.
 * It does not attach listeners, read keys/text, schedule timers, write files,
 * invoke models or tools, or exercise any operating-system input permission.
 * Callers must obtain consent and supply ONLY event class + monotonic time.
 */

export const SCHEMA = 'CoOmniIO.CoInputGap.Shadow.R0';
const PROPOSALS = Object.freeze([
  'INSPECT_RELATIONS',
  'CHALLENGE_PREMISE',
  'COMPARE_PRIOR_VERSION',
]);
const RESTRICTED_FIELDS = Object.freeze([
  'key', 'code', 'text', 'raw', 'clipboard', 'password', 'selectedText',
  'windowTitle', 'screen', 'content', 'prompt', 'url', 'path',
]);
function assertObject(o) {
  if (!o || typeof o !== 'object' || Array.isArray(o)) throw new TypeError('event must be an object');
  for (const name of RESTRICTED_FIELDS) {
    if (Object.hasOwn(o, name)) throw new TypeError('raw/sensitive event field forbidden');
  }
}
function assertTime(t) {
  if (!Number.isSafeInteger(t) || t < 0) throw new TypeError('time must be a nonnegative monotonic integer');
}
function proposal(kind, why) {
  return Object.freeze({ schema: SCHEMA, status: kind, proposed_action: null,
    reason: why, effects: Object.freeze({ keys_captured: 0, text_saved: 0, workers_spawned: 0, messages_sent: 0 }) });
}
export class InputGapShadow {
  constructor({ quietMs = 800, minEdits = 2, cooldownMs = 3000 } = {}) {
    if (!Number.isSafeInteger(quietMs) || quietMs < 300 || quietMs > 20000 ||
        !Number.isSafeInteger(minEdits) || minEdits < 1 || minEdits > 20 ||
        !Number.isSafeInteger(cooldownMs) || cooldownMs < 1000 || cooldownMs > 60000) {
      throw new TypeError('bounded finite configuration required');
    }
    this.quietMs = quietMs;
    this.minEdits = minEdits;
    this.cooldownMs = cooldownMs;
    this.armed = false;
    this.lastTime = null;
    this.lastEdit = null;
    this.lastProposal = null;
    this.pendingEdits = 0;
    this.totalProposals = 0;
    this.awaitingDecision = false;
  }
  #time(t) {
    assertTime(t);
    if (this.lastTime !== null && t < this.lastTime) throw new RangeError('clock went backward');
    this.lastTime = t;
  }
  arm({ consent = false, scope = '', atMs = 0, sensitive = false } = {}) {
    assertTime(atMs);
    if (consent !== true || scope !== 'OWNED_EDITOR' || sensitive !== false) {
      this.disarm(); return proposal('HOLD_NOT_ARMED', 'explicit consent and owned nonsensitive editor required');
    }
    this.disarm();
    this.armed = true;
    this.lastTime = atMs;
    return proposal('ARMED_LOCAL_SHADOW', 'no global hooks or raw text access');
  }
  disarm() {
    this.armed = false;
    this.lastTime = null;
    this.lastEdit = null;
    this.lastProposal = null;
    this.pendingEdits = 0;
    this.awaitingDecision = false;
    return proposal('DISARMED', 'state cleared; no event observer installed');
  }
  note(event) {
    assertObject(event);
    const { kind, atMs, focused = true, sensitive = false } = event;
    this.#time(atMs);
    if (!this.armed) return proposal('HOLD_NOT_ARMED', 'no opt-in');
    if (focused !== true || sensitive !== false || kind === 'FOCUS_LOST') {
      this.disarm(); return proposal('DISARMED_PRIVATE_OR_UNFOCUSED', 'private or out of scope');
    }
    if (kind === 'CANCEL') return this.disarm();
    if (kind !== 'LOCAL_EDIT' && kind !== 'LOCAL_POINTER') {
      return proposal('HOLD_UNKNOWN_EVENT', 'unrecognized activity');
    }
    if (kind === 'LOCAL_EDIT') {
      this.pendingEdits = Math.min(this.pendingEdits + 1, this.minEdits);
      this.lastEdit = atMs;
      this.awaitingDecision = false;
    }
    return proposal('SHADOW_UPDATED', 'event class counted, raw keys/text not supplied');
  }
  inspect({ atMs, focused = true, sensitive = false, scope = 'OWNED_EDITOR' } = {}) {
    this.#time(atMs);
    if (!this.armed) return proposal('HOLD_NOT_ARMED', 'no opt-in');
    if (focused !== true || sensitive !== false || scope !== 'OWNED_EDITOR') {
      this.disarm(); return proposal('DISARMED_PRIVATE_OR_UNFOCUSED', 'no probing outside owned editor');
    }
    if (this.awaitingDecision) return proposal('HOLD_AWAITING_DECISION', 'explicit decision required');
    if (this.lastEdit === null || this.pendingEdits < this.minEdits) {
      return proposal('HOLD_INSUFFICIENT_LOCAL_ACTIVITY', 'cannot infer intent from empty gap');
    }
    if (atMs - this.lastEdit < this.quietMs) return proposal('HOLD_QUIET_WINDOW', 'not enough quiet time');
    if (this.lastProposal !== null && atMs - this.lastProposal < this.cooldownMs) {
      return proposal('HOLD_COOLDOWN', 'anti-nag cooldown');
    }
    const type = PROPOSALS[this.totalProposals % PROPOSALS.length];
    this.awaitingDecision = true;
    this.lastProposal = atMs;
    this.totalProposals++;
    this.pendingEdits = 0;
    return Object.freeze({ ...proposal('CANDIDATE_ONLY', 'quiet time indicates readiness to preview, not user intent'),
      proposed_action: type, accepted: false, confidence: 'UNASSESSED',
      authority: 'NONE', privacy: 'OWNED_EDITOR_ONLY' });
  }
  decide({ atMs, decision } = {}) {
    this.#time(atMs);
    if (!this.armed || !this.awaitingDecision) return proposal('HOLD_NO_PENDING_PROPOSAL', 'no pending choice');
    if (decision !== 'ACCEPT_PREVIEW' && decision !== 'REJECT_PREVIEW') {
      return proposal('HOLD_BAD_DECISION', 'only explicit accept or reject');
    }
    this.awaitingDecision = false;
    return proposal(decision === 'ACCEPT_PREVIEW' ? 'PREVIEW_ACCEPTED_ONLY' : 'PREVIEW_REJECTED',
      'choice recorded in memory only; no execution authority');
  }
  status() {
    return Object.freeze({ schema: SCHEMA, armed: this.armed, edits_capped: this.pendingEdits,
      proposal_count: this.totalProposals, awaiting_decision: this.awaitingDecision,
      content_retained: false, listener_installed: false, effects: 'NONE' });
  }
}
