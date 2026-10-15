import re
import unicodedata
from datetime import date
from urllib.parse import quote


def safe_part(value: str) -> str:
    value = unicodedata.normalize("NFKC", str(value)).strip()
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]+", "-", value)
    value = re.sub(r"[^\w .()\-À-ỹぁ-んァ-ヶ一-龯]+", "-", value, flags=re.UNICODE)
    return re.sub(r"[- ]+", "-", value).strip(".-") or "ho-so"


def export_filename(customer, project, kind, version=1, export_date=None, ext=None):
    ext = ext or kind
    export_date = export_date or date.today().isoformat()
    return f"{safe_part(customer)}_{safe_part(project)}_{safe_part(kind)}_v{int(version)}_{export_date}.{ext}"


def content_disposition(filename: str) -> str:
    """RFC 6266 header: ASCII fallback plus UTF-8 name (HTTP headers must stay latin-1)."""
    ascii_name = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
    ascii_name = re.sub(r'[\s"\\;]+', "-", ascii_name).strip("-") or "export"
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}"
