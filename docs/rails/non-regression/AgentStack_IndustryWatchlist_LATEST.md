# Agent-Stack Industry Watchlist (feeds MasterPlan gates)
UTC: 20260216T143440Z

This is not “news.” It is an ongoing checklist for *non-regressive* MasterPlan evolution.

## 1) Standards / foundations to track
- Linux Foundation AAIF: donated agent standards (MCP, AGENTS.md, Goose) intended to stay open/neutral/community-driven.
  Sources:
  - WIRED (AAIF launch context): https://www.wired.com/story/openai-anthropic-and-block-are-teaming-up-on-ai-agent-standards
  - ITPro (MCP donation + AAIF framing): https://www.itpro.com/software/open-source/anthropic-says-mcp-will-stay-open-neutral-and-community-driven-after-donating-project-to-linux-foundation

## 2) Current “agent supply-chain” failure modes
- Malicious skills / extensions marketplaces (agent tools as the new browser extension problem).
  Example incident reporting:
  - The Hacker News (OpenClaw / ClawHub ecosystem report): https://thehackernews.com/2025/02/openclaw-exposes-new-crypto.html

## 3) Prompt-injection & tool-arg poisoning
- Treat all retrieved text as hostile; enforce origin scoping; implement negative tests for “run/install/exfiltrate” patterns.
  Primary guidance:
  - OpenAI (Prompt injection): https://openai.com/index/prompt-injection

## 4) Framework mappings your CI should explicitly cover
- OWASP Top 10 for LLM Applications (map tests to categories):
  - https://owasp.org/www-project-top-10-for-large-language-model-applications/
- MITRE ATLAS (agentic threat techniques + TTP vocabulary):
  - https://atlas.mitre.org/
- NIST AI RMF 1.0 (govern/measure/manage scaffolding):
  - https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf

## 5) MasterPlan gate deltas to enforce (tie to your G0–G9 doc)
- G0: pin-by-SHA everywhere + receipts.
- G1: capability ladder default DENY; no broadened defaults without evidence.
- G3: injection regression suite must include tool-arg poisoning cases.
- G5: replayable traces + hashes for tool calls.
- G8: kill-switch / rollback drills must be runnable and evidenced.
