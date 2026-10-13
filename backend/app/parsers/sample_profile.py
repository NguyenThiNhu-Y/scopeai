import re
def profile(rows: list[dict]) -> dict:
    names = sorted({k for row in rows for k in row})
    cols=[]
    for name in names:
        vals=[row.get(name) for row in rows]; nonempty=[v for v in vals if v not in (None, "")]
        kind="number" if nonempty and all(isinstance(v,(int,float)) for v in nonempty) else "string"
        cols.append({"name":name,"type":kind,"empty_pct":round((len(vals)-len(nonempty))*100/len(vals)) if vals else 0,"pii_suspected":bool(re.search(r"email|phone|điện|tel|連絡先|メール|電話",name,re.I))})
    empty=sum(c["empty_pct"] for c in cols)/len(cols) if cols else 0
    return {"row_count":len(rows),"columns":cols,"readiness_suggestion":"low" if empty>30 else ("medium" if empty>10 else "high")}
