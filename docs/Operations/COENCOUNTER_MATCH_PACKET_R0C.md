# CoEncounter exact match-packet pickup + contribution lineage R0C

**State:** `PASS_BOUNDED_CONTAINER_LOCAL_SYNTHETIC__EXACT_PACKET_PICKUP__PROPOSED_LINEAGE__NO_AUTO_ASSIGNMENT`

R0C advances the landed R0B Open Relation routing proof by taking exactly one `MATCH_CANDIDATE`, compiling an exact receiver packet, requiring the elected receiver to read the exact packet bytes before `PICKED_UP`, and binding a subsequent proposed contribution into an appendable lineage object without pretending it has been accepted or integrated.

## Lifecycle

`MATCH_CANDIDATE -> EXACT_PACKET -> RECEIVER_READPROOF -> PICKED_UP_BOUNDED -> CONTRIBUTION_PROPOSED -> LINEAGE_BOUND`

The packet is not picked up merely because it exists. The receiver process must bind its own identity to the exact packet SHA-256 and full-object read.

`DELIVERY_NE_PICKUP`

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

The bounded canary proves pickup for one synthetic receiver packet only. It does not prove semantic acceptance, integration, a distinct failure domain, live runtime adoption, or public effect.

## Contribution lineage

After pickup, the canary creates one proposed contribution candidate and binds:

- match packet;
- receiver readproof;
- proposed contribution;
- the Open Relation it responds to.

It deliberately leaves `acceptance_relation = null` and `integration_relation = null`.

`LINEAGE_NE_ACCEPTANCE`

`PROPOSED_NE_ACCEPTED`

`ATTRIBUTION_NE_OWNERSHIP`

If a later receiver accepts a contribution, acceptance should be appended as a new evidenced relation rather than rewriting the earlier provenance chain.

## Bounded execution evidence

Before execution, the R0A encounter fixture, R0B receiver fixture, and R0B reviewer were rebound to their exact current-main Git blob identities:

- encounter fixture blob `41979591241ec277e6f51a72b93340a7f61c332e`;
- receiver fixture blob `a29a2979a85e5f4c121109f9616e789f05285704`;
- R0B reviewer blob `3f3bbc1f7b0a2cec009e6d6f16f8dc6318d84745`.

Those source blobs remained unchanged on current public main after `7b08c68bae6ec76c33d70eabbd5afa1a2e41429b`.

The exact candidate branch scripts were then read back and executed. The canary produced:

- exact match packet SHA-256 `99A60F2B48D1DE524C570FF333B60D72BBE622B213EF33C8D858216179539A2B`;
- separate compiler / receiver / lineage process IDs `885 / 895 / 905`;
- one receiver-produced exact packet readproof;
- one bounded `PICKED_UP` transition for that packet;
- one proposed contribution lineage object;
- zero assignment, notification, authority, execution, provider-session, semantic-acceptance or integration effects.

Evidence: `docs/Operations/proofs/coencounter-r0c-container-pass-20260924.json`.

## Next

`R0D_SEMANTIC_CONTRIBUTION_DISPOSITION_OR_HETEROGENEOUS_RECEIVER_PACKET_CANARY__NO_AUTO_ASSIGNMENT`

The next rung should either obtain a separately evidenced semantic disposition on the proposed contribution or run the exact packet through a genuinely heterogeneous receiver. It should not treat process multiplicity as failure-domain or model-family independence.

## Rails

`PICKED_UP_NE_INTEGRATED`  
`READPROOF_NE_SEMANTIC_ACCEPTANCE`  
`LINEAGE_NE_ACCEPTANCE`  
`MATCH_NE_ASSIGNMENT_AUTHORITY`  
`PACKET_NE_EXECUTION_AUTHORITY`  
`TWO_OR_MORE_PROCESSES_NE_TWO_OR_MORE_FAILURE_DOMAINS`  
`LOCAL_CANARY_NE_RUNTIME_INTEGRATION`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
