"""Service hồ sơ mẫu giả lập — FR-006 phần 1 (contract api_contract.md §3.7).

Dữ liệu 100% hư cấu (BR-06): tên công ty/khách hàng giả, file mẫu có header
"DỮ LIỆU GIẢ LẬP". Mỗi mẫu chứa email + SĐT để minh chứng mask PII khi gửi LLM.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.api.errors import validation_error
from app.models import Attachment, Bid
from app.parsers.detect import detect_type

def _find_sample_dir() -> Path:
    """Tìm thư mục ``sample_data`` — robust với mọi layout (dev, container).

    Duyệt từ file hiện tại lên các cấp cha; chỉ chấp nhận thư mục thực sự
    chứa file mẫu (tránh thư mục ``sample_data`` rỗng còn sót).
    """
    candidates = [Path("/sample_data")]
    candidates.extend(parent / "sample_data" for parent in Path(__file__).resolve().parents)
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "ja_email.md").is_file():
            return candidate
    raise RuntimeError("Không tìm thấy thư mục sample_data chứa file mẫu")


_SAMPLE_DIR = _find_sample_dir()

_SAMPLES: dict[str, dict] = {
    "ja_email": {
        "project_name": "顧客管理システム（CRM）構築支援（サンプル・架空）",
        "customer_name": "株式会社デモ商事（仮名・架空）",
        "submission_deadline": "2026-12-15",
        "customer_language": "ja",
        "display_currency": "JPY",
        "budget_amount": 15000000,
        "budget_currency": "JPY",
        "customer_schedule_start": "2027-01-01",
        "customer_schedule_end": "2027-09-30",
            "file": "ja_email.md",
            "attachments": [("ja_rfp.docx", "rfp"), ("ja_requirements.xlsx", "requirement")],
    },
    "vi_email": {
        "project_name": "Hệ thống quản lý kho (dữ liệu giả lập)",
        "customer_name": "Công ty TNHH Minh Phát (giả lập)",
        "submission_deadline": "2026-12-20",
        "customer_language": "vi",
            "file": "vi_email.md",
            "attachments": [("requirements_sample.csv", "requirement"), ("sample_data_sample.csv", "sample_data")],
    },
}


def sample_preview(sample_key: str = "ja_email") -> dict:
    """Trả metadata để người dùng xem bộ mẫu trước khi tạo hồ sơ."""
    meta = _SAMPLES.get(sample_key)
    if meta is None:
        raise validation_error(
            f"Mẫu giả lập '{sample_key}' không tồn tại",
            {"sample_key": sample_key, "allowed": sorted(_SAMPLES)},
        )
    files = [(meta["file"], "rfp")]
    files.extend(meta.get("attachments", []))
    return {
        "sample_key": sample_key,
        "project_name": meta["project_name"],
        "customer_name": meta["customer_name"],
        "submission_deadline": meta["submission_deadline"],
        "customer_language": meta["customer_language"],
        "display_currency": meta.get("display_currency") or (
            "JPY" if meta["customer_language"] == "ja" else "VND"
        ),
        "budget_amount": meta.get("budget_amount"),
        "budget_currency": meta.get("budget_currency"),
        "customer_schedule_start": meta.get("customer_schedule_start"),
        "customer_schedule_end": meta.get("customer_schedule_end"),
        "request_content": (_SAMPLE_DIR / meta["file"]).read_text(encoding="utf-8").strip(),
        "files": [
            {
                "filename": filename,
                "file_type": file_type,
                "size_bytes": (_SAMPLE_DIR / filename).stat().st_size,
            }
            for filename, file_type in files
        ],
    }


def load_sample(
    session: Session, sample_key: str = "ja_email", created_by: str = "anonymous"
) -> Bid:
    """Đọc file mẫu và tạo hồ sơ mới ở trạng thái ``draft``."""
    meta = _SAMPLES.get(sample_key)
    if meta is None:
        raise validation_error(
            f"Mẫu giả lập '{sample_key}' không tồn tại",
            {"sample_key": sample_key, "allowed": sorted(_SAMPLES)},
        )
    path = _SAMPLE_DIR / meta["file"]
    content = path.read_text(encoding="utf-8").strip()

    bid = Bid(
        project_name=meta["project_name"],
        customer_name=meta["customer_name"],
        submission_deadline=date.fromisoformat(meta["submission_deadline"]),
        customer_language=meta["customer_language"],
        display_currency=meta.get("display_currency") or (
            "JPY" if meta["customer_language"] == "ja" else "VND"
        ),
        request_content=content,
        budget_amount=meta.get("budget_amount"),
        budget_currency=meta.get("budget_currency"),
        customer_schedule_start=(
            date.fromisoformat(meta["customer_schedule_start"])
            if meta.get("customer_schedule_start")
            else None
        ),
        customer_schedule_end=(
            date.fromisoformat(meta["customer_schedule_end"])
            if meta.get("customer_schedule_end")
            else None
        ),
        created_by=created_by,
    )
    session.add(bid)
    session.commit()
    session.refresh(bid)
    upload_root = Path("data/uploads") / str(bid.id)
    upload_root.mkdir(parents=True, exist_ok=True)
    for attachment_name, file_type in meta.get("attachments", []):
        attachment_path = _SAMPLE_DIR / attachment_name
        data = attachment_path.read_bytes()
        stored_path = upload_root / attachment_name
        stored_path.write_bytes(data)
        detected = detect_type(attachment_name, data)
        session.add(Attachment(
            bid_id=bid.id,
            filename=attachment_name,
            file_type=file_type,
            detected_type=detected,
            size_bytes=len(data),
            path=str(stored_path),
        ))
    session.commit()
    return bid
