/* CoCivium first-contact local card R1.
 * No network, telemetry, persistent browser storage, remote effects or auto-import.
 * Review-only source candidate. File input reads bytes solely after user selection.
 */
(function (environment) {
  'use strict';

  var TITLE = '# My first useful CoCivium card';
  var STATUS = 'Status: LOCAL_DRAFT__NOT_SUBMITTED__NOT_VERIFIED';
  var GOAL = '\n## Goal\n';
  var PROOF = '\n## Evidence I would look for\n';
  var NEXT = '\n## One safe next step\n';
  var SOURCE_R0 = 'Source: CoCivium CoSpiff first-contact R0';
  var SOURCE_R1 = 'Source: CoCivium CoSpiff first-contact R1';
  var MAX_FIELD = 1000;
  var MAX_FILE_BYTES = 12288;

  function fail(reason) {
    throw new Error(reason);
  }

  function formatCard(goal, proof) {
    goal = String(goal).trim();
    proof = String(proof).trim();
    if (!goal || !proof || goal.length > MAX_FIELD || proof.length > MAX_FIELD) {
      fail('HOLD_CARD_FIELD_BOUNDS');
    }
    if (/(^|\n)## /m.test(goal) || /(^|\n)## /m.test(proof)) {
      fail('HOLD_CARD_RESERVED_HEADING');
    }
    return [
      TITLE, '', STATUS, '', '## Goal', goal, '',
      '## Evidence I would look for', proof, '',
      '## One safe next step',
      'Try the smallest reversible version. Record what changed, what failed, and how to undo it.',
      '', '## Privacy and authority',
      'Prepared locally. No account, remote execution, external submission, or authority transfer.',
      '', SOURCE_R1
    ].join('\n') + '\n';
  }

  function parseCard(text) {
    if (typeof text !== 'string') {
      fail('HOLD_CARD_TEXT_REQUIRED');
    }
    // UTF-8 inputs are bounded in bytes again before Browser File.text().
    if (text.length > MAX_FILE_BYTES) {
      fail('HOLD_CARD_TOO_LARGE');
    }
    var normalized = text.replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
    if (normalized.indexOf('\r') !== -1) {
      fail('HOLD_CARD_LINE_ENDING');
    }
    // Source status is machine-owned header state, not a token that can
    // be supplied later in user text to counterfeit a receiver ACK.
    var expectedHeader = [TITLE, '', STATUS, ''].join('\n') + '\n';
    if (!normalized.startsWith(expectedHeader) ||
        !(normalized.trimEnd().endsWith(SOURCE_R0) ||
          normalized.trimEnd().endsWith(SOURCE_R1))) {
      fail('HOLD_CARD_PROVENANCE');
    }
    for (var marker of [GOAL, PROOF, NEXT]) {
      if (normalized.split(marker).length !== 2) {
        fail('HOLD_CARD_STRUCTURE');
      }
    }
    var g = normalized.indexOf(GOAL);
    var p = normalized.indexOf(PROOF);
    var n = normalized.indexOf(NEXT);
    if (!(g > 0 && p > g && n > p)) {
      fail('HOLD_CARD_SECTION_ORDER');
    }
    var goal = normalized.slice(g + GOAL.length, p).trim();
    var proof = normalized.slice(p + PROOF.length, n).trim();
    if (!goal || !proof || goal.length > MAX_FIELD || proof.length > MAX_FIELD) {
      fail('HOLD_CARD_FIELD_BOUNDS');
    }
    if (/(^|\n)## /m.test(goal) || /(^|\n)## /m.test(proof)) {
      fail('HOLD_CARD_RESERVED_HEADING');
    }
    return {goal: goal, proof: proof, provenance: normalized.trimEnd().endsWith(SOURCE_R0) ? 'R0' : 'R1'};
  }

  // Node's test runner imports the exact parser without creating a DOM or effects.
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {formatCard: formatCard, parseCard: parseCard};
  }

  if (!environment || !environment.document) {
    return;
  }
  var document = environment.document;
  var form = document.getElementById('card-form');
  var goalField = document.getElementById('goal');
  var proofField = document.getElementById('proof');
  var restore = document.getElementById('restore-file');
  var status = document.getElementById('status');
  if (!form || !goalField || !proofField || !restore || !status) {
    return;
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var source;
    try {
      source = formatCard(goalField.value, proofField.value);
    } catch (error) {
      status.textContent = 'Complete both fields within 1,000 characters. Remove Markdown section headings before saving.';
      return;
    }
    var blob = new Blob([source], {type: 'text/markdown;charset=utf-8'});
    var url = URL.createObjectURL(blob);
    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'cocivium-my-first-card.md';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    status.textContent = 'Local card generated. Check your browser downloads. Nothing was submitted.';
  });

  restore.addEventListener('change', async function () {
    var file = restore.files && restore.files[0];
    if (!file) {
      return;
    }
    try {
      if (goalField.value.trim() || proofField.value.trim()) {
        fail('HOLD_EXISTING_CARD_NOT_OVERWRITTEN');
      }
      if (file.size > MAX_FILE_BYTES || file.size === 0) {
        fail('HOLD_CARD_FILE_SIZE');
      }
      var fields = parseCard(await file.text());
      goalField.value = fields.goal;
      proofField.value = fields.proof;
      status.textContent = 'Local ' + fields.provenance + ' card restored in this tab. Review it before saving. Nothing was uploaded.';
      goalField.focus();
    } catch (error) {
      status.textContent = 'Restore held: invalid, oversized, or incompatible card, or existing text would be overwritten. Your form was not changed.';
    } finally {
      // Permit the same file to be selected again; retain no file reference.
      restore.value = '';
    }
  });
})(typeof window === 'undefined' ? null : window);
