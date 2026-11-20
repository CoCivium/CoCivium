"use strict";
/**
 * CoCI+ separate-job artifact readback canary R0.
 *
 * Reads an immutable source job artifact downloaded into this GitHub Actions
 * job.  Confirms commit, complete manifest membership, exact source SHA-256,
 * executed regression counts and negative controls.  No remote device, ET,
 * fiction, private manuscript or external effect is accessed.
 *
 * A CI readback is NOT an independent provider/failure-domain receiver ACK.
 */
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");

const repo = path.resolve(__dirname, "..");
const artifact = path.resolve(process.argv[2] || path.join(repo, "artifacts/comegathesis-r0"));
const output = path.resolve(process.argv[3] || path.join(repo, "artifacts/comegathesis-readback-r0"));
const sha256 = b => crypto.createHash("sha256").update(b).digest("hex");

const SOURCE_PATHS = [
  "scripts/test_comegathesis_three_view_r0.cjs",
  "ai/cotheoryall/comegathesis-relations-r0.json",
  "ai/cotheoryall/comegathesis-mythos-federation-delta-r0.json",
  "docs/CoTheoryAll/candidates/comegathesis-reader-r0.html",
  "docs/CoTheoryAll/candidates/COMYTHOS_COSEEDUNIFY_COFED_COIGC_R0_20261120.md"
];
const REPLAY_PATHS = ["scripts/test_coworkid_process_replay_r0.cjs"];
const CONCURRENT_PATHS = ["scripts/test_coworkid_concurrent_fencing_r0.cjs"];
const RESIDUE_PATHS = [
  "scripts/test_coci_session_residue_r0.cjs",
  "ai/currentness/coci-session-noncycling-checkpoint-r0-20261120.json",
  "ai/currentness/coci-session-residue-gates-r0-20261120.json"
];
const INPUT_FILES = [
  "source-hashes.sha256",
  "coworkid-process-replay.sha256",
  "revision.txt",
  "source-tests.log",
  "coworkid-process-replay.log",
  "nonclaims.txt",
  "coworkid-concurrent-fence.sha256",
  "coworkid-concurrent-fence.log",
  "session-residue.sha256",
  "session-residue.log"
];

function sourcePath(rel) {
  assert.equal(typeof rel, "string");
  assert(!path.posix.isAbsolute(rel) && !rel.includes("\\") && !rel.includes("\0"));
  assert(!rel.split("/").some(seg => seg === "" || seg === "." || seg === ".."));
  const abs = path.resolve(repo, rel);
  assert(abs.startsWith(repo + path.sep), "HOLD_SOURCE_PATH_ESCAPE");
  const real = fs.realpathSync(abs);
  assert(real.startsWith(repo + path.sep), "HOLD_SOURCE_SYMLINK_ESCAPE");
  return real;
}
function verifyManifest(content, expectedPaths) {
  const entries = content.trimEnd().split("\n").map((line) => {
    const m = /^([0-9a-f]{64})  ([^\r\n]+)$/.exec(line);
    assert(m, "HOLD_MALFORMED_SHA256_MANIFEST");
    sourcePath(m[2]);
    return { sha256: m[1], path: m[2] };
  });
  assert.deepEqual(entries.map(e => e.path), expectedPaths, "HOLD_MANIFEST_MEMBER_DRIFT");
  for (const entry of entries) {
    const actual = sha256(fs.readFileSync(sourcePath(entry.path)));
    assert.equal(actual, entry.sha256, "HOLD_HASH_MISMATCH_" + entry.path);
  }
  return entries;
}
function countPasses(text) {
  return text.split(/\r?\n/).filter(s => s.startsWith("PASS ")).length;
}
function verify(i) {
  const commit = execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim();
  assert.match(commit, /^[a-f0-9]{40}$/);
  assert.equal(i.revision.trim(), commit, "HOLD_REPLAY_WRONG_REVISION");
  if (process.env.GITHUB_SHA) assert.equal(process.env.GITHUB_SHA, commit, "HOLD_RUN_HEAD_DRIFT");

  const sourceEntries = verifyManifest(i.sourceManifest, SOURCE_PATHS);
  const replayEntries = verifyManifest(i.replayManifest, REPLAY_PATHS);
  const concurrentEntries = verifyManifest(i.concurrentManifest, CONCURRENT_PATHS);
  const residueEntries = verifyManifest(i.residueManifest, RESIDUE_PATHS);

  assert.equal(countPasses(i.sourceLog), 11, "HOLD_SOURCE_TEST_COUNT");
  assert(i.sourceLog.includes("SOURCE_ONLY_PASS 11 tests"), "HOLD_SOURCE_TEST_RESULT_ABSENT");
  assert.equal(countPasses(i.replayLog), 17, "HOLD_RECOVERY_TEST_COUNT");
  assert(i.replayLog.includes("SYNTHETIC_SOURCE_RECOVERY_PASS 17 tests"), "HOLD_RECOVERY_TEST_RESULT_ABSENT");
  assert(i.replayLog.includes("no independent receiver"), "HOLD_RECOVERY_NONCLAIM_ABSENT");
  assert.equal(countPasses(i.concurrentLog), 16, "HOLD_CONCURRENT_TEST_COUNT");
  assert(i.concurrentLog.includes("SYNTHETIC_CONCURRENT_FENCE_PASS 16 tests"), "HOLD_CONCURRENT_RESULT_ABSENT");
  assert(i.concurrentLog.includes("NO_POWER_LOSS_PROOF"), "HOLD_CONCURRENT_SCOPE_ABSENT");
  assert.equal(countPasses(i.residueLog), 20, "HOLD_RESIDUE_TEST_COUNT");
  assert(i.residueLog.includes("NONCYCLING_RESIDUE_SOURCE_ONLY_PASS 20 tests"), "HOLD_RESIDUE_RESULT_ABSENT");
  assert(i.residueLog.includes("all_sessions=false provider_chat_archived=false receiver_ack=false"), "HOLD_RESIDUE_NONCLAIM_ABSENT");
  assert(i.nonclaims.includes("DOES_NOT_PROVE_BROWSER_UX_RUNTIME_RECEIVER_COEX_CANON_OR_DEPLOYMENT"), "HOLD_CI_NONCLAIM_ABSENT");
  return { commit, sourceEntries, replayEntries, concurrentEntries, residueEntries };
}

function expectHold(name, mutation, input) {
  let didHold = false;
  try { verify(mutation(input)); }
  catch (_err) { didHold = true; }
  assert(didHold, "NEGATIVE_CONTROL_DID_NOT_HOLD_" + name);
  process.stdout.write("PASS fail-closed " + name + "\n");
}

const data = {};
const inputNames = {
  sourceManifest: INPUT_FILES[0], replayManifest: INPUT_FILES[1],
  revision: INPUT_FILES[2], sourceLog: INPUT_FILES[3],
  replayLog: INPUT_FILES[4], nonclaims: INPUT_FILES[5],
  concurrentManifest: INPUT_FILES[6], concurrentLog: INPUT_FILES[7],
  residueManifest: INPUT_FILES[8], residueLog: INPUT_FILES[9]
};
for (const [k, filename] of Object.entries(inputNames)) {
  const located = path.join(artifact, filename);
  assert(located.startsWith(artifact + path.sep), "HOLD_INPUT_ESCAPE");
  data[k] = fs.readFileSync(located, "utf8");
}
const verified = verify(data);
const negative = [
  ["stale_revision", d => ({ ...d, revision: "0".repeat(40) })],
  ["source_digest_tamper", d => ({ ...d, sourceManifest: d.sourceManifest.replace(/^[a-f0-9]{64}/, "0".repeat(64)) })],
  ["source_membership_drop", d => ({ ...d, sourceManifest: d.sourceManifest.split("\n").slice(1).join("\n") })],
  ["manifest_path_traversal", d => ({ ...d, sourceManifest: d.sourceManifest.replace(SOURCE_PATHS[0], "../escape.cjs") })],
  ["missing_source_pass", d => ({ ...d, sourceLog: d.sourceLog.replace("SOURCE_ONLY_PASS 11 tests", "SOURCE_ONLY_RESULT_UNKNOWN") })],
  ["source_log_pass_count", d => ({ ...d, sourceLog: d.sourceLog.replace(/^PASS .+\r?\n/m, "") })],
  ["missing_recovery_pass", d => ({ ...d, replayLog: d.replayLog.replace("SYNTHETIC_SOURCE_RECOVERY_PASS 17 tests", "RECOVERY_RESULT_UNKNOWN") })],
  ["missing_nonclaims", d => ({ ...d, nonclaims: "" })],
  ["concurrent_digest_tamper", d => ({ ...d, concurrentManifest: d.concurrentManifest.replace(/^[a-f0-9]{64}/, "0".repeat(64)) })],
  ["concurrent_result_removed", d => ({ ...d, concurrentLog: d.concurrentLog.replace("SYNTHETIC_CONCURRENT_FENCE_PASS 16 tests", "UNKNOWN") })],
  ["residue_digest_tamper", d => ({ ...d, residueManifest: d.residueManifest.replace(/^[a-f0-9]{64}/, "0".repeat(64)) })],
  ["residue_result_removed", d => ({ ...d, residueLog: d.residueLog.replace("NONCYCLING_RESIDUE_SOURCE_ONLY_PASS 20 tests", "UNKNOWN") })]
];
for (const [name, mutate] of negative) expectHold(name, mutate, data);

fs.mkdirSync(output, { recursive: true });
const receipt = {
  schema: "CoCI.CrossJobArtifactReadback.R0",
  status: "GITHUB_CI_JOB_SCOPED_SOURCE_READBACK_PASS",
  observed_at_utc: new Date().toISOString(),
  github_run_id: process.env.GITHUB_RUN_ID || null,
  github_job: process.env.GITHUB_JOB || null,
  source_commit: verified.commit,
  source_job: "source-parity",
  receiving_job: "artifact-readback",
  received_artifact_name: "comegathesis-source-proof-" + (process.env.GITHUB_RUN_ID || "UNKNOWN"),
  tests: { source: 11, process_recovery: 17, concurrent_fencing: 16, session_residue: 20, negative_controls: negative.length },
  exact_manifest_paths: {
    source: verified.sourceEntries.map(x => x.path),
    replay: verified.replayEntries.map(x => x.path),
    concurrent: verified.concurrentEntries.map(x => x.path),
    session_residue: verified.residueEntries.map(x => x.path)
  },
  received_artifact_file_hashes: Object.fromEntries(
    INPUT_FILES.map(name => [name, sha256(fs.readFileSync(path.join(artifact, name)))])
  ),
  receiver_boundary: {
    distinct_github_actions_job: true,
    github_control_plane_shared: true,
    different_power_domain: "NOT_INDEPENDENTLY_VERIFIED",
    receiver_is_cocivium_runtime: false,
    effect: "READ_ONLY_VERIFICATION_OF_GITHUB_CI_ARTIFACT"
  },
  nonclaims: [
    "CI_ARTIFACT_PICKUP_NE_COSTEAD_OR_X2_RECEIVER_PICKUP",
    "SEPARATE_GITHUB_JOB_NE_INDEPENDENT_PROVIDER",
    "PROCESS_REPLAY_NE_DURABLE_POWER_FAILURE_RECOVERY",
    "CI_PASS_NE_HUMAN_UX_ACCEPTANCE",
    "CI_SOURCE_NE_CANON_OR_COEX_OR_DEPLOYMENT",
    "NO_EXTERNAL_EFFECT_OR_AUTHORITY_EXPANSION"
  ]
};
const receiptPath = path.join(output, "coci-artifact-readback-receipt.json");
fs.writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + "\n", { flag: "wx" });
fs.writeFileSync(path.join(output, "coci-artifact-readback-receipt.sha256"),
  sha256(fs.readFileSync(receiptPath)) + "  coci-artifact-readback-receipt.json\n",
  { flag: "wx" });
process.stdout.write("CI_ARTIFACT_READBACK_PASS source=11 replay=17 concurrent=16 residue=20 negatives=" + negative.length + " provider_independent=false\n");
