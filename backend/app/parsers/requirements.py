ALIASES = {
    "code": ("no", "id", "要件id", "要件ＩＤ", "mã", "ma"),
    "content": ("要件内容", "内容", "requirement", "description", "nội dung", "機能要件"),
    "name": ("要件名", "requirement name", "tên"),
    "priority": ("優先度", "priority", "ưu tiên"),
}


def _find_column(row: dict, kind: str, mapping: dict) -> str | None:
    if mapping.get(kind):
        return mapping[kind]
    aliases = ALIASES[kind]
    for key in row:
        normalized = str(key).strip().lower()
        if normalized in aliases or any(alias in normalized for alias in aliases):
            return key
    return None


def normalize(sheets: dict[str,list[dict]], mappings: dict[str,dict] | None = None, used_codes: set[str] | None = None) -> list[dict]:
    result=[]
    for sheet, rows in sheets.items():
        mapping=(mappings or {}).get(sheet,{})
        for row_no,row in enumerate(rows,2):
            content_key = _find_column(row, "content", mapping)
            content=str(row.get(content_key,"" ) or "").strip() if content_key else ""
            if not content: continue
            code_key = _find_column(row, "code", mapping)
            raw=row.get(code_key) if code_key else None
            code=str(raw).strip() if raw is not None and not (isinstance(raw,str) and raw.startswith("=")) else ""
            result.append({"internal_code":code,"content":content,"priority":row.get(_find_column(row, "priority", mapping) or ""),"category":row.get(mapping.get("category")) if mapping.get("category") else None,"source_sheet":sheet,"source_row":row.get("__row__", row_no),"source_cols":row})
    # used_codes: tập mã đã dùng CHUNG cho nhiều file đính kèm — mã dự phòng
    # REQ-xxx không được trùng giữa các file (unique (bid_id, internal_code)).
    used=used_codes if used_codes is not None else set()
    for i,item in enumerate(result,1):
        if not item["internal_code"] or item["internal_code"] in used:
            candidate=f"REQ-{len(used)+1:03d}"
            suffix=1
            while candidate in used:
                suffix += 1
                candidate=f"REQ-{len(used)+1:03d}-{suffix}"
            item["internal_code"]=candidate
        used.add(item["internal_code"])
    return result
