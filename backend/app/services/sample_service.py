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


def _tokai_attachments() -> list[tuple[str, str]]:
    """4 tệp thật của bộ Tokai trong ``real/`` — khớp theo đuôi file.

    Tên trên đĩa có thể lệch chuẩn Unicode (NFC/NFD), nên không khớp chuỗi
    cứng; mỗi đuôi chỉ có đúng một tệp trong thư mục real/. Trả về đường dẫn
    TƯƠNG ĐỐI từ ``_SAMPLE_DIR`` (giống các bộ mẫu khác).
    """
    real_rel = Path("rfp_tokai_minato") / "real"
    real_dir = _SAMPLE_DIR / real_rel
    by_ext: dict[str, str] = {}
    for path in sorted(real_dir.glob("*")):
        if path.is_file():
            by_ext.setdefault(path.suffix.lower(), str(real_rel / path.name))
    expected = {".docx": "rfp", ".xlsx": "requirement", ".csv": "sample_data", ".pdf": "rfp"}
    missing = sorted(set(expected) - set(by_ext))
    if missing:
        raise RuntimeError(f"Thiếu tệp thật của bộ Tokai trong {real_dir}: {missing}")
    return [(by_ext[ext], file_type) for ext, file_type in expected.items()]


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
    # Bộ mẫu Tokai Minato (giả lập) — RAG bảo trì, PoC trước (thiet_ke_danh_gia.md §6).
    "tokai_minato": {
        "project_name": "設備保全ナレッジAIアシスタント構築（PoC）（サンプル・架空）",
        "customer_name": "株式会社東海ミナトテック（架空）",
        "submission_deadline": "2026-10-30",
        "customer_language": "ja",
        "display_currency": "JPY",
        "budget_amount": 15000000,
        "budget_currency": "JPY",
        "budget_scope": "poc",
        "customer_schedule_start": "2026-12-01",
        "customer_poc_end": "2027-02-28",
        "customer_mvp_start": "2027-04-01",
        "customer_production_start": "2027-10-01",
        "file": "rfp_tokai_minato/email_yeu_cau_khach.txt",
        "attachments": _tokai_attachments(),
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
        budget_scope=meta.get("budget_scope"),
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
        customer_poc_end=(
            date.fromisoformat(meta["customer_poc_end"])
            if meta.get("customer_poc_end")
            else None
        ),
        customer_mvp_start=(
            date.fromisoformat(meta["customer_mvp_start"])
            if meta.get("customer_mvp_start")
            else None
        ),
        customer_production_start=(
            date.fromisoformat(meta["customer_production_start"])
            if meta.get("customer_production_start")
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
        stored_name = Path(attachment_name).name
        stored_path = upload_root / stored_name
        stored_path.write_bytes(data)
        detected = detect_type(stored_name, data)
        session.add(Attachment(
            bid_id=bid.id,
            filename=stored_name,
            file_type=file_type,
            detected_type=detected,
            size_bytes=len(data),
            path=str(stored_path),
        ))
    session.commit()
    return bid
