import re
import unicodedata


def safe_part(value: str) -> str:
    value = unicodedata.normalize("NFKC", str(value)).strip()
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]+", "-", value)
    value = re.sub(r"[^\w .()\-À-ỹぁ-んァ-ヶ一-龯]+", "-", value, flags=re.UNICODE)
    return re.sub(r"[- ]+", "-", value).strip(".-") or "ho-so"


def export_filename(customer, project, kind, version=1, export_date="2026-10-10", ext=None):
    ext = ext or kind
    return f"{safe_part(customer)}_{safe_part(project)}_{safe_part(kind)}_v{int(version)}_{export_date}.{ext}"
