# Security Policy

CoCivium is in a public R&D / pre-launch transition.

## Reporting

Please do **not** publish credentials, private keys, tokens, private personal data, or a working exploit containing sensitive material in a public issue.

For a suspected vulnerability, use the repository's private security-reporting mechanism when available. If that mechanism is unavailable, use the current public contact route listed by CoCivium and include only the minimum information needed to establish contact; sensitive details should follow through a suitably private channel.

## Scope

Public prototypes, StrawBe+ objects, research hypotheses, and demos may be incomplete. That does not make credential exposure, privacy leaks, unsafe defaults, or privilege-escalation behavior acceptable.

Useful reports include:

- credential/secret exposure;
- unauthorized data disclosure;
- unsafe filesystem/process effects;
- permission escalation;
- cross-user or cross-node leakage;
- supply-chain compromise;
- misleading security/currentness indicators;
- prompt/content injection that can cross an authority boundary;
- destructive behavior without an explicit gate.

## Nonclaims

A passing scanner is not proof of security.

`SECURITY_SCANNER_NE_SECURITY_PROOF`  
`PUBLIC_NE_PERMISSION_TO_ATTACK_PRODUCTION_OR_PRIVATE_SYSTEMS`  
`REPORT_NE_PUBLIC_DISCLOSURE_AUTHORIZATION`
