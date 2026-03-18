# CoBus Attach Rules v1

## STATES
bootstrapped
read_attached
write_attached
fully_hitched
blocked
local_receipt_only

## ENFORCEMENT
- Local files → local_receipt_only
- RAW URLs → read only
- write_attached requires:
  - repo commit
  - public RAW URL
- fully_hitched requires:
  - read-after-write verification

## FAIL-CLOSED
If uncertain → degrade state

