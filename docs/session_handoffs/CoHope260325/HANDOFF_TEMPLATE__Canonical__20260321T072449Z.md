<# FROM=<SOURCE_SESSION> TO=<TARGET_SESSION>,CoPrime,ACTIVE_SESSIONS UTC=<UTC_ISO> STATE=handoff_backup_salute INTENT=Carry forward only verified state, canonical pins, explicit open work, and one next anchoring wave ACTION=
1) TRUTHFUL_HITCH_STATE=<read_attached|write_attached|fully_hitched>
2) PINS_ONLY=
   - CoBeacon=<RAW_URL>
   - Broadcast=<RAW_URL>
   - Registry=<RAW_URL>
   - CoPrimeScope=<RAW_URL>
   - BootstrapRollup=<RAW_URL>
3) LAST_VERIFIED_WRITE=
   - Surface=<repo/vault/path>
   - Pointer=<raw/path>
   - HashOrCommit=<value>
4) LANDED=
   - <exact artifact 1>
   - <exact artifact 2>
5) OPEN_WORK=
   - required=<items>
   - optional=<items>
   - inspirational=<items>
6) NEXT_ANCHOR=
   - artifact=<single named artifact>
   - action=<single verifiable mutation>
   - success_condition=<hash/commit/raw>
7) UNVERIFIED_BELIEFS=
   - <things believed but not proven>
#>
