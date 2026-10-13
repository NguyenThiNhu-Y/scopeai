from pathlib import Path
ALLOWED = {".pdf", ".docx", ".txt", ".md", ".xlsx", ".xlsm", ".csv", ".xls"}
def detect_type(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED: raise ValueError("Định dạng file không được hỗ trợ")
    if ext in {".xlsx", ".xlsm", ".xls"}: return "requirement"
    if ext == ".csv":
        # CSV is used for both requirements and operational history. Keep the
        # existing requirement default while recognizing the fixture/export
        # naming used for fault-history data as a sample profile.
        stem = Path(filename).stem.casefold()
        if any(token in stem for token in ("fault", "failure", "故障", "障害", "履歴")):
            return "sample_data"
        return "requirement"
    return "rfp"
