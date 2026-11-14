// CoCopy/CoBar CoPaste R0. Isolated, owner-controlled text-field insertion only.
// No clipboard read/write, keyboard simulation, implicit submit, network, or persistence.
'use strict';

function createCoPasteR0({maxCodeUnits=200000}={}) {
  const committed = new Map();
  const busy = new WeakSet();
  const hold = (state) => Object.freeze({state, insertion_calls:0, sent:false});

  function validateTarget(target, expectedTargetId) {
    if (!target || typeof target !== 'object') return 'HELD_TARGET_MISSING';
    if (target.id !== expectedTargetId || !expectedTargetId) return 'HELD_WRONG_TARGET';
    if (target.dataset?.copasteOwned !== 'true') return 'HELD_TARGET_NOT_OWNED';
    if (!['TEXTAREA', 'INPUT'].includes(String(target.tagName||'').toUpperCase())) return 'HELD_UNSUPPORTED_TARGET';
    if (String(target.tagName).toUpperCase()==='INPUT' &&
      !['text','search'].includes(String(target.type||'text').toLowerCase())) return 'HELD_UNSUPPORTED_TARGET';
    if (target.disabled || target.readOnly || typeof target.setRangeText!=='function') return 'HELD_READ_ONLY';
    if (!target.ownerDocument || target.ownerDocument.activeElement!==target) return 'HELD_FOCUS_CHANGED';
    return null;
  }

  function insert({target, expectedTargetId, requestId, payload, authorized, expectedValue}={}) {
    if (authorized!==true) return hold('HELD_NOT_AUTHORIZED');
    if (typeof requestId!=='string' || !/^[a-zA-Z0-9._:-]{1,100}$/.test(requestId)) return hold('HELD_REQUEST_ID');
    if (typeof payload!=='string' || payload.length>maxCodeUnits) return hold('HELD_PAYLOAD');
    const invalid=validateTarget(target,expectedTargetId);
    if (invalid) return hold(invalid);
    if (busy.has(target)) return hold('HELD_TARGET_BUSY');
    const old=committed.get(requestId);
    if (old) {
      if (old.target!==target || old.payload!==payload || old.targetId!==expectedTargetId) return hold('HELD_REQUEST_CONFLICT');
      return hold(target.value===old.after?'DUPLICATE_SUPPRESSED':'HELD_DESTINATION_CHANGED');
    }
    const before=target.value;
    if (typeof before!=='string' || expectedValue!==before) return hold('HELD_PRESTATE_CHANGED');
    const start=target.selectionStart, end=target.selectionEnd;
    if (!Number.isInteger(start) || !Number.isInteger(end) || start<0 || end<start || end>before.length) return hold('HELD_SELECTION');
    const after=before.slice(0,start)+payload+before.slice(end);
    if (after.length>maxCodeUnits || (Number.isInteger(target.maxLength) && target.maxLength>=0 && after.length>target.maxLength)) return hold('HELD_LENGTH');
    busy.add(target);
    try {
      // One native-field operation; not per-character typing. Application-host integration
      // must choose its own state synchronization, receipt, and separately authorized Send.
      target.setRangeText(payload,start,end,'end');
      if (target.value!==after) return Object.freeze({state:'HELD_READBACK_MISMATCH',insertion_calls:1,sent:false});
      committed.set(requestId,{target,targetId:expectedTargetId,payload,before,after});
      return Object.freeze({state:'INSERTED_VERIFIED_TEXT_VALUE',insertion_calls:1,length:after.length,sent:false});
    } catch (_error) {
      return Object.freeze({state:'FAILED_INSERT_EXCEPTION',insertion_calls:1,sent:false});
    } finally {
      busy.delete(target);
    }
  }

  function undo({target,expectedTargetId,requestId,authorized}={}) {
    if (authorized!==true) return hold('HELD_NOT_AUTHORIZED');
    const invalid=validateTarget(target,expectedTargetId);
    if (invalid) return hold(invalid);
    const old=committed.get(requestId);
    if (!old || old.target!==target || old.targetId!==expectedTargetId) return hold('HELD_NO_MATCHING_INSERT');
    if (target.value!==old.after) return hold('HELD_DESTINATION_CHANGED');
    if (busy.has(target)) return hold('HELD_TARGET_BUSY');
    busy.add(target);
    try {
      target.setRangeText(old.before,0,target.value.length,'end');
      if (target.value!==old.before) return Object.freeze({state:'HELD_UNDO_READBACK_MISMATCH',insertion_calls:1,sent:false});
      committed.delete(requestId);
      return Object.freeze({state:'UNDO_VERIFIED_TEXT_VALUE',insertion_calls:1,sent:false});
    } catch (_error) {
      return Object.freeze({state:'FAILED_UNDO_EXCEPTION',insertion_calls:1,sent:false});
    } finally {
      busy.delete(target);
    }
  }

  return Object.freeze({insert,undo});
}
if (typeof module!=='undefined' && module.exports) module.exports={createCoPasteR0};
