# CoUX Refresh Trigger Canary R0A

**State:** `PASS_LOCAL_ONE_SHOT_SOURCE_CHANGE_TO_PROJECTION_READBACK__VISIBLE_UI_READBACK_UNPROVEN`

## Bound local proof

On X2, a bounded one-shot watcher canary observed a synthetic source change from revision 1 to revision 2, rebuilt a receiver projection, then read the projection back from disk.

Source root:

`D:\CoCivium\CoFarm\CoUXCurrentness261002-S1\R0A_trigger_canary`

Observed receipt:

- state: `PASS_SOURCE_CHANGE_TO_PROJECTION_READBACK`
- projection SHA-256: `C00011E870A076DBDB32EA5A1B395F71935728D4AB3E6F483C575730DD3606DE`
- receipt SHA-256: `023F0955034F09E6019517140FDF1EE4039E09B0187F4746797C326984EB58E7`
- elapsed time: `4868 ms`
- visible UI readback: `false`
- persistent watcher installed: `false`

## Meaning

This advances the acceptance ladder from:

`SOURCE_CURRENTNESS_BOUND -> PROJECTION_COMPILED`

to a bounded local proof of:

`SOURCE_CHANGE_OBSERVED -> PROJECTION_REBUILT -> LOCAL_FILE_READBACK`

It does **not** yet prove:

- RickBar/CoBar visible render changed;
- human observer saw the new state;
- a persistent or production refresh service exists;
- event-driven refresh rather than bounded polling;
- runtime adoption;
- CoBar continuity-root status changed.

## Why one-shot first

The canary is deliberately non-persistent. It proves the trigger/rebuild relation without installing another daemon before the receiver contract is proven.

`ONE_SHOT_TRIGGER_NE_DAEMON`

`LOCAL_FILE_READBACK_NE_HUMAN_VISIBLE_READBACK`

`PROJECTION_REBUILD_NE_VISIBLE_RENDER`

## Next rung

The next earned proof is:

`LOCAL_PROJECTION -> EXISTING_RICKBAR_RECEIVER_PICKUP -> VISIBLE_RENDER -> OBSERVER_READBACK`

without making the receiver itself the source of truth.

## Rails

`ONE_SHOT_TRIGGER_NE_DAEMON`  
`PROJECTION_REBUILD_NE_VISIBLE_RENDER`  
`LOCAL_FILE_READBACK_NE_HUMAN_VISIBLE_READBACK`  
`CANARY_NE_RUNTIME_ADOPTION`  
`COBAR_NE_CONTINUITY_ROOT`  
`VALIDATION_IS_NOT_ACCEPTANCE`
