ALIASES = {
    "code": ("no", "id", "要件id", "要件ＩＤ", "mã", "ma", "code"),
    "content": ("要件内容", "内容", "requirement", "description", "nội dung", "機能要件", "content"),
    "name": ("要件名", "requirement name", "tên"),
    "priority": ("優先度", "priority", "ưu tiên"),
}


def _find_column(row: dict, kind: str, mapping: dict) -> str | None:
    if mapping.get(kind):
        return mapping[kind]
    aliases = ALIASES[kind]
    # Ưu tiên khớp CHÍNH XÁC trước (vd cột "要件ID" phải thắng cột "No." dù
    # alias "no" là chuỗi con của "No.") — Đợt 14, giữ mã requirement của khách.
    normalized = {str(key).strip().lower(): key for key in row}
    for alias in aliases:
        if alias in normalized:
            return normalized[alias]
    for key in row:
        normalized_key = str(key).strip().lower()
        if any(alias in normalized_key for alias in aliases):
            return key
    return None


def normalize(sheets: dict[str,list[dict]], mappings: dict[str,dict] | None = None, used_codes: set[str] | None = None) -> list[dict]:
    result=[]
    # Sheet nào có cột mã requirement (要件ID/ID/No.)? Sheet bìa/hướng dẫn
    # (vd 表紙) không có cột mã → bỏ khi file có sheet khác có cột mã (Đợt 14).
    mappings = mappings or {}
    code_keys: dict[str, str | None] = {}
    for sheet, rows in sheets.items():
        mapping = mappings.get(sheet, {})
        code_keys[sheet] = _find_column(rows[0], "code", mapping) if rows else None
    has_code_anywhere = any(code_keys.values())
    for sheet, rows in sheets.items():
        if not rows:
            continue
        if has_code_anywhere and code_keys[sheet] is None:
            continue
        mapping = mappings.get(sheet, {})
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
