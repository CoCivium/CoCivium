#!/usr/bin/env python3
"""CoTermable operator-expression fixture R0. No CoLex mutation or runtime effect.

A syntactic operator expression is a *question or working candidate*, not a newly
registered word, an observation of sentience, a consent grant, or an action.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
import json

ROOTS = {
    "coregroup": {"label":"CoRegroup+", "kind":"PROCESS", "source":"docs/Architecture/COBOOGIE_REGROUP_RELATIONAL_RETURN_R1.md"},
    "coboogie": {"label":"CoBoogie+", "kind":"PROCESS", "source":"docs/Architecture/COBOOGIE_REGROUP_RELATIONAL_RETURN_R1.md"},
    "coglyphrail": {"label":"CoGlyphRail+", "kind":"PROCESS", "source":"docs/broadcasts/COEVOALL_EVERGREEN_BLAST__20261023.md"},
    "colex": {"label":"CoLex+", "kind":"KNOWLEDGE", "source":"docs/coterms/README.md"},
    "coagent": {"label":"CoAgent+", "kind":"SYSTEM", "source":"docs/Books/AGI_For_Beginners/README.md"},
}
OPERATORS = {
    "AUTO": {"arity":1,"input_kinds":["PROCESS"],"output_kind":"PROCESS","meaning":"What bounded parts could be automated under separate authorization?"},
    "SENTIENT?": {"arity":1,"input_kinds":["SYSTEM"],"output_kind":"HYPOTHESIS","meaning":"Which discriminating evidence bears on possible experience? No assertion of sentience."},
    "SAME?": {"arity":2,"input_kinds":["ANY"],"output_kind":"HYPOTHESIS","meaning":"Equivalent in a specified context, sense and time? No global identity merge."},
    "COSCENDENT": {"arity":1,"input_kinds":["PROCESS","SYSTEM"],"output_kind":"HYPOTHESIS","meaning":"Could this cross declared frames with translation loss audited? No status hierarchy."},
    "DOOFERATE": {"arity":1,"input_kinds":["ANY"],"output_kind":"PROJECTION","meaning":"Could a lossy compact view help a receiver? Preserve exact-source return."},
    "NULL": {"arity":1,"input_kinds":["ANY"],"output_kind":"HYPOTHESIS","meaning":"What does a no-effect/control baseline predict?"},
    "INVERSE?": {"arity":1,"input_kinds":["ANY"],"output_kind":"HYPOTHESIS","meaning":"What reverse hypothesis is meaningful, without manufacturing an inverse fact?"}
}
EFFECTS = "NONE"
NONCLAIMS = [
    "EXPRESSION_NE_REGISTERED_COTERM", "SENTIENT_LABEL_NE_CONSCIOUSNESS",
    "AUTO_LABEL_NE_ACTUATION", "SAME_QUESTION_NE_IDENTITY",
    "COSCENDENT_NE_SUPERIORITY", "POWDERED_VIEW_NE_EXACT_BYTES",
    "COMBINATORIAL_SPACE_NE_ACTIVE_EXECUTION", "NAME_NE_AUTHORITY"
]
def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"))
def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()
def root(identifier):
    if identifier not in ROOTS:
        raise ValueError("UNKNOWN_SOURCE_BOUND_ROOT")
    return {"node":"ROOT","id":identifier, **ROOTS[identifier]}

def _checked(node):
    if not isinstance(node, dict):
        raise ValueError("UNTRUSTED_OPERAND")
    if node.get("node")=="ROOT":
        if node!=root(node.get("id")):
            raise ValueError("FORGED_ROOT_OR_MEANING")
        return node["kind"],node["label"],1
    if node.get("node")!="EXPR" or node.get("authority")!=EFFECTS:
        raise ValueError("FORGED_EXPRESSION_OR_AUTHORITY")
    op=node.get("operator")
    if op not in OPERATORS or not isinstance(node.get("operands"),list):
        raise ValueError("BAD_EXPRESSION")
    params=node.get("params")
    reconstructed=compose(op,*node["operands"],params=params)
    if node != reconstructed:
        raise ValueError("EXPRESSION_SIGNATURE_OR_CONTENT_MISMATCH")
    return OPERATORS[op]["output_kind"],node["display"],node["depth"]

def compose(operator,*operands,params=None):
    if operator not in OPERATORS:
        raise ValueError("UNKNOWN_OPERATOR")
    spec=OPERATORS[operator]
    if len(operands)!=spec["arity"]:
        raise ValueError("OPERATOR_ARITY")
    if params is None:
        params={}
    if not isinstance(params,dict) or any(k not in ("context","from_frame","to_frame") for k in params):
        raise ValueError("UNKNOWN_OR_INVALID_CONTEXT")
    validated=[_checked(n) for n in operands]
    depth=1+max(d[2] for d in validated)
    if depth>3:
        raise ValueError("COMPOSITION_DEPTH_BUDGET")
    for kind,_,_ in validated:
        if "ANY" not in spec["input_kinds"] and kind not in spec["input_kinds"]:
            raise ValueError("INCOMPATIBLE_OPERATOR_KIND")
    if operator=="SAME?":
        if not isinstance(params.get("context"),str) or not params["context"].strip():
            raise ValueError("SAME_REQUIRES_CONTEXT")
        if operands[0]==operands[1]:
            raise ValueError("SAME_TAUTOLOGY_NOT_NOVELTY")
    if operator=="COSCENDENT":
        if not all(isinstance(params.get(k),str) and params[k].strip() for k in ("from_frame","to_frame")):
            raise ValueError("CROSS_FRAME_REQUIRED")
        if params["from_frame"]==params["to_frame"]:
            raise ValueError("CROSS_FRAME_MUST_DIFFER")
    if operator not in ("SAME?","COSCENDENT") and params:
        raise ValueError("OPERATOR_CONTEXT_NOT_APPLICABLE")
    # The strings are a display projection; the expression tree is the identity.
    display=operator+"("+", ".join(v[1] for v in validated)+")"
    if operator=="COSCENDENT":
        display+="["+params["from_frame"]+" -> "+params["to_frame"]+"]"
    if operator=="SAME?":
        display+="["+params["context"]+"]"
    payload={"node":"EXPR","operator":operator,"operands":list(operands),
             "params":params,"authority":EFFECTS,"depth":depth,
             "epistemic_class":"HYPOTHESIS","display":display}
    payload["expression_id"]=digest(payload)
    return payload

def candidates(source_ids,operators,limit=8):
    """Lazy finite first ring. No global compound materialization or effects."""
    if not isinstance(limit,int) or isinstance(limit,bool) or not 0<=limit<=32:
        raise ValueError("CANDIDATE_LIMIT")
    if not isinstance(source_ids,(list,tuple)) or not isinstance(operators,(list,tuple)):
        raise ValueError("DECLARED_INPUTS_REQUIRED")
    yielded=0
    for rid,op in product(source_ids,operators):
        if yielded>=limit:
            return
        try:
            c=compose(op,root(rid))
        except ValueError:
            continue
        yielded+=1
        yield c

def dooferate(data:bytes,source_id:str,preview_bytes:int=24):
    """A short lossy view. A digest is for *verification*, never reconstruction."""
    if not isinstance(data,bytes) or not isinstance(source_id,str) or not source_id.strip():
        raise ValueError("SOURCE_BYTES_AND_ID_REQUIRED")
    if not isinstance(preview_bytes,int) or isinstance(preview_bytes,bool) or not 0<=preview_bytes<=64:
        raise ValueError("PREVIEW_BUDGET")
    return {"source_id":source_id, "source_sha256":sha256(data).hexdigest(),
            "preview_hex":data[:preview_bytes].hex(),
            "omitted_byte_count":len(data)-min(len(data),preview_bytes),
            "fidelity":"LOSSY", "no_original_embedded":True,
            "status":"VIEW_ONLY_NOT_CUSTODY"}
def rehydrate(card,sources):
    """Only recovers by reading the surviving source. Fail closed on missing bytes."""
    if not isinstance(card,dict) or not isinstance(sources,dict):
        raise ValueError("MISSING_OR_INVALID_MATERIAL")
    b=sources.get(card.get("source_id"))
    if not isinstance(b,bytes):
        raise ValueError("SOURCE_UNAVAILABLE_NOT_RECONSTRUCTABLE")
    if sha256(b).hexdigest()!=card.get("source_sha256"):
        raise ValueError("SOURCE_MISMATCH")
    return b

def demo():
    sample=[
        compose("AUTO",root("coregroup")),
        compose("SENTIENT?",root("coagent")),
        compose("SAME?",root("coboogie"),root("coregroup"),params={"context":"workflow role, 2026"}),
        compose("COSCENDENT",root("coglyphrail"),params={"from_frame":"TEXT","to_frame":"VOICE"}),
        compose("DOOFERATE",root("colex")),
        compose("NULL",root("coregroup")),
    ]
    data=b"Synthetic source: a word has a stable identity while meanings evolve."
    return {"schema":"CoAll.CoTermableOperatorExpression.R0-SYNTHETIC",
            "state":"READ_ONLY_NO_LEXICON_MUTATION",
            "sources":sorted(ROOTS),
            "operators":sorted(OPERATORS),
            "examples":[{"expression_id":x["expression_id"],"display":x["display"],"meaning":OPERATORS[x["operator"]]["meaning"],"status":"CANDIDATE_ONLY"} for x in sample],
            "powdered_view":dooferate(data,"fixture:colex"),
            "rehydration_with_source":rehydrate(dooferate(data,"fixture:colex"),{"fixture:colex":data})==data,
            "rehydration_without_source":"EXPECTED_HOLD",
            "actual_effects":0,
            "human_adoption":"NOT_TESTED",
            "nonclaims":NONCLAIMS}
if __name__=="__main__":
    print(json.dumps(demo(),ensure_ascii=False,sort_keys=True,indent=2))
