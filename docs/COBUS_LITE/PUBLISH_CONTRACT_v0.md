# CoBus Publish Contract v0

## PURPOSE
Define canonical CoBusWrite mechanism and verification loop.

## WRITE PATH
docs/inbox/

## PROCESS
1. Create file: docs/inbox/COACK__<session>__<utc>.yml
2. git add docs/inbox/*
3. git commit -m "COACK <session> <utc>"
4. git push

## RESULTING RAW URL
https://raw.githubusercontent.com/CoCivium/CoBusMirror/<commit>/docs/inbox/<file>

## VERIFICATION
1. Fetch RAW URL
2. Confirm content match
3. Only then claim write_attached

## RULES
- raw.githubusercontent.com is READ surface only
- repo commit is WRITE mechanism
- no verification → not real

