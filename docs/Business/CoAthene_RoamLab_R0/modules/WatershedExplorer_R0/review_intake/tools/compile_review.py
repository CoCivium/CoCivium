import json
import re
import sys
from pathlib import Path

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

def sections(text):
    matches=list(SECTION_RE.finditer(text))
    out={}
    for i,m in enumerate(matches):
        start=m.end()
        end=matches[i+1].start() if i+1 < len(matches) else len(text)
        out[m.group(1).strip()]=text[start:end].strip()
    return out

def defect_fields(block):
    names=["DEFECT","WHERE","WHY_IT_MATTERS","EVIDENCE_OR_EXAMPLE","SUGGESTED_FIX","SEVERITY","CONFIDENCE"]
    positions=[]
    for name in names:
        mm=re.search(rf"(?m)^{re.escape(name)}:\s*", block)
        if mm:
            positions.append((mm.start(), mm.end(), name))
    positions.sort()
    out={}
    for i,(start,value_start,name) in enumerate(positions):
        end=positions[i+1][0] if i+1 < len(positions) else len(block)
        out[name]=block[value_start:end].strip()
    return out

def compile_review(text):
    s=sections(text)
    material=s.get("10. Material defects","")
    df=defect_fields(material)
    return {
        "schema":"CoAthene.ReviewDerivedDefect.v0.1-candidate",
        "reviewer_context":{
            "role":s.get("Reviewer role",""),
            "experience":s.get("Relevant experience",""),
            "jurisdiction":s.get("Jurisdiction",""),
            "conflict_disclosure":s.get("Connection or conflict disclosure",""),
        },
        "reviewer_disposition":s.get("11. Final disposition",""),
        "reviewer_confidence":s.get("Confidence in your overall review",""),
        "defect":{
            "summary":df.get("DEFECT",""),
            "where":df.get("WHERE",""),
            "why_it_matters":df.get("WHY_IT_MATTERS",""),
            "evidence_or_example":df.get("EVIDENCE_OR_EXAMPLE",""),
            "suggested_fix":df.get("SUGGESTED_FIX",""),
            "severity":df.get("SEVERITY",""),
            "confidence":df.get("CONFIDENCE",""),
        },
        "project_disposition":"UNSET_REQUIRES_SEPARATE_TRIAGE",
        "rails":[
            "RAW_REVIEW_NE_DERIVED_DEFECT",
            "REVIEWER_CLAIM_NE_PROJECT_FACT",
            "STRUCTURED_REVIEW_NE_TRUTH",
            "DISPOSITION_NE_REVIEWER_AGREEMENT"
        ]
    }

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: compile_review.py REVIEW.md")
    text=Path(sys.argv[1]).read_text(encoding="utf-8")
    print(json.dumps(compile_review(text),indent=2,ensure_ascii=False))
