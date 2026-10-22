# CoResearchContinuity+ candidate contract
Date: 2026-10-22
Status: PROPOSAL. Not implemented, tested, landed in durable CoStead custody, or integrated into runtime. This branch is a review surface.

## Goal
Make research survive session interruptions and preserve resource options, evidence, counterevidence, uncertainty, and exact resumption state.

## CoGlueKeys+ envelope
session_id; question_id; claim_id; object_id; revision; event_cursor; policy_version; lease_id; lease_expires_at; checkpoint_id; source_refs; conflict_refs; last_observed_at; receiver_ack.
Keep UNKNOWN, ABSENT, FALSE, STALE, NOT_OBSERVED, NOT_APPLICABLE, FORBIDDEN distinct.

## CoResourceAtlas+ selection
For each candidate source/tool/model/device/method record resource_id, capability, authorization, observed availability and time, privacy boundary, freshness, independence, cost, latency, failure mode, fallback, selected/deferred/rejected rationale. Record what was not searched and why. Never claim exhaustive discovery.

## CoResearchGate+ Extraordinary
G0 claim identity and scope; G1 primary observations; G2 prior art; G3 independent corroboration; G4 adversarial counterevidence; G5 prospective falsifiers; G6 independent replication; G7 domain-specific closure. Preserve source identity, dates, uncertainty and receipts. Do not promote extraordinary claims without domain-specific verification.

## CoLUE+ choice
Select the next bounded deed using expected decision value, uncertainty reduction, independence, authority, resource budget, reversibility and recoverability. Preserve dissent and alternative substrates/renders/surfaces.

## First acceptance test
Two sessions share an object and revision. Writer commits a controlled change. Reader is interrupted, resumes from stale checkpoint and event cursor, detects the revision difference, preserves conflict, verifies provenance, and obtains receiver ACK. Inject missing ACK and unavailable resource cases. Require independently reproducible logs and receipts.

## Boundaries
Proposal != implementation; GitHub pointer != durable landing; render != state; heartbeat != wisdom; receipt != receiver benefit. No implied background execution or authorization for spending, bulk publication, privacy-sensitive access or irreversible actions.
