# CoCivium first-contact safe-page R0

**CANDIDATE ONLY | PRE-LAUNCH | NOT DEPLOYED | NO PRODUCTION CHANGE**

A small, standalone HTML entrance that avoids a firehose of terminology. It gives a visitor one locally generated, downloadable first-use card, then source-linked optional paths into CoPreCursor+, resource discovery, evidence, and public issue challenges. No login, cookie storage, fetch, tracking service, third-party asset or background execution is requested by the page. Links to GitHub are initiated by the visitor and follow GitHub's own data practices.

## Test and provenance boundary

Checked October 24, 2026, in a local, non-production container:

- Exact candidate `index.html` SHA-256: `8571ded6bb4bd1d9f2a7e91681b998e2425358a16a4604be592fc6abeb67ea69`.
- 11/11 bounded static-source checks passed.
- 5/5 adversarial/offline unit checks passed, including intentionally bad local path, remote script, tracking API and release-language fixtures.
- 14/14 bounded headless Chromium checks passed across desktop/mobile, local Markdown download, error handling, and no observed requests.
- These are local self-tests. This branch does not contain the full test harness or a remotely produced receiver acceptance; the originating review package retains its scripts, outputs and screenshots.

A source-verified, local browser check is **not** a production deploy, rights audit, independent accessibility audit, security certification, DNS/TLS acceptance, off-provider cold restore, or successful independent user experience.

## Independent review gates, proportional to risk

1. **Source and priors:** match links to current GitHub blob/version; verify wording and explicit unsupported claims.
2. **Security/authority:** review the approved public artifact allowlist, privacy classification, inherited licensing, rollback operator, CSP and no private-metadata leakage. Preserve incident details privately.
3. **Accessibility and usability:** keyboard, screen reader, mobile, consent, language, and first useful outcome with an unfamiliar participant.
4. **Operations and recovery:** a qualified owner identifies actual DNS/CDN configuration, clean reversibility, both apex/www checks and two independent network probes. Separately test second-provider cold restore, not just two GitHub URLs.
5. **Adversarial CoTurtle:** test that the tests reject known-bad fixtures; preserve negative cases and finite depth, time and budget limits.
6. **Release stewardship:** independently authorized reviewer adjudicates the evidence, retains dissent, and elects any production promotion.

This is a proposed replacement **candidate** for review, not an instruction to overwrite the current site. A public GitHub branch does not prove a custom-domain front door is repaired.

**Related existing roots:** [START_HERE](https://github.com/CoCivium/CoCivium/blob/main/START_HERE.md), [EVERGREEN](https://github.com/CoCivium/CoCivium/blob/main/EVERGREEN.md), [CoSpiff+ 14-gate assessment](https://github.com/CoCivium/CoCivium/blob/main/ai/resilience/cospiff-fireworks-r1.json). Do not create another authority ledger when these already exist.

## Outstanding release and provider tests

HELD/NOT QUALIFIED: independent first-use, site HTTP/TLS and private metadata review, independent off-provider restore, CoStead readproof, Gmail Primary timing, ID-provider proof, Pi.dev/other Pi compatibility timing, Claude credential-health timing, Ollama/Llama packet parse on X2, ffprobe/blackdetect (no video fixture), hardware thumb remapping, public 200/p95 latency, and repeat adoption. Source branch and self-test evidence do not promote any of these.
