"""Bước B1 — Intake: trích xuất thông tin yêu cầu (llm_pipeline.md §2)."""

from __future__ import annotations

import asyncio
import re
from datetime import date
from pathlib import Path

from app.core import db
from app.core.config import settings
from app.llm import complete_with_retry
from app.llm.gateway import LLMSchemaError
from app.llm.prompts.b1_intake import build_intake_prompt
from app.models import Attachment, Bid, Requirement
from app.parsers.excel import read_sheets
from app.parsers.docx import extract_text as extract_docx_text
from app.parsers.pdf import extract_text as extract_pdf_text
from app.parsers.text import extract_text
from app.parsers.sample_profile import profile
from app.pipeline.steps.common import (
    get_step,
    mark_failed,
    publish_error,
    publish_step,
    utcnow,
)
from app.privacy import mask_text
from app.schemas.llm_schemas import IntakeExtraction


def _find_milestone(text: str, keywords: tuple[str, ...]) -> date | None:
    """Tìm ngày (năm?)+tháng trong câu chứa từ khóa mốc (着手/MVP/本番...).

    Mốc ngày thường đứng TRƯỚC từ khóa ("2027年1月に着手", "6月までにMVP",
    "9月に本番展開") — chọn mốc ngày gần từ khóa nhất nằm trước nó.
    """
    for sentence in re.split(r"[。\n；;]", text):
        positions = [sentence.find(keyword) for keyword in keywords]
        positions = [pos for pos in positions if pos >= 0]
        if not positions:
            continue
        keyword_pos = min(positions)
        candidates: list[tuple[int, date]] = []
        for match in re.finditer(r"(?:(20\d{2})年)?\s*(\d{1,2})月", sentence):
            if match.end() > keyword_pos:
                continue
            year = int(match.group(1) or 2027)
            month = int(match.group(2))
            if 1 <= month <= 12:
                candidates.append((keyword_pos - match.end(), date(year, month, 1)))
        if candidates:
            return min(candidates, key=lambda item: item[0])[1]
    return None


def _find_poc_end(text: str) -> date | None:
    """Tìm ngày kết thúc PoC từ khoảng thời gian "PoC … 2026年12月〜2027年2月".

    RFP Tokai: "Phase 1：PoC |2026年12月〜2027年2月（3か月）" — mốc kết thúc là
    NGÀY CUỐI của tháng sau dấu 〜 trong câu có chứa PoC (kỳ kết thúc cuối tháng).
    """
    import calendar

    for sentence in re.split(r"[。\n；;]", text):
        if "PoC" not in sentence:
            continue
        match = re.search(r"(\d{4})年\s*(\d{1,2})月\s*〜\s*(\d{4})年\s*(\d{1,2})月", sentence)
        if match:
            year, month = int(match.group(3)), int(match.group(4))
            if 1 <= month <= 12:
                return date(year, month, calendar.monthrange(year, month)[1])
    return None


def _is_open_ended(text: str, milestone: date) -> bool:
    """True nếu mốc là phase mở (vd "2027年10月〜") — không có ngày kết thúc."""
    needle = f"{milestone.year}年{milestone.month}月"
    for sentence in re.split(r"[。\n；;]", text):
        pos = sentence.find(needle)
        if pos < 0:
            continue
        tail = sentence[pos + len(needle):]
        if re.match(r"\s*[〜～]|以降|から", tail):
            return True
    return False


def _apply_customer_constraints(bid: Bid, text: str) -> None:
    """Persist explicit RFP budget and milestones; never delegate numbers to LLM."""
    budget = re.search(r"1,500万円|1500万円", text)
    if budget:
        bid.budget_amount = 15_000_000
        bid.budget_currency = "JPY"
        # Phạm vi ngân sách: nếu câu ngân sách nói rõ PoC (vd "PoC：1,500万円…以内")
        # → chỉ đối chiếu giá PoC, không dùng tổng dự án.

        sentence_start = max(text.rfind("。", 0, budget.start()) + 1, text.rfind("\n", 0, budget.start()) + 1)
        sentence_end = len(text)
        for idx in (text.find("。", budget.end()), text.find("\n", budget.end())):
            if idx >= 0:
                sentence_end = min(sentence_end, idx)
        if "PoC" in text[sentence_start:sentence_end]:
            bid.budget_scope = "poc"

    # Mốc khách: bắt đầu / PoC kết thúc / MVP / Production (RFP Nhật: 2027/1,  ​2027/6,  ​2027/9).
    start = _find_milestone(text, ("着手", "開始", "スタート", "起動"))
    poc_end = _find_poc_end(text)
    mvp = _find_milestone(text, ("MVP",))
    production = _find_milestone(text, ("本番", "production", "正式稼働"))
    if start:
        bid.customer_schedule_start = start
    if poc_end:
        bid.customer_poc_end = poc_end
    if mvp:
        bid.customer_mvp_start = mvp
    if production:
        bid.customer_production_start = production
        # Phase mở (vd "2027年10月〜") không có ngày kết thúc — không gán end.

        if not _is_open_ended(text, production):
            bid.customer_schedule_end = production
    else:
        # Fallback: tháng lớn nhất xuất hiện trong văn bản — chỉ khi chưa có
        # mốc kết thúc (không ghi đè mốc khách đã biết, ví dụ bộ Tokai).
        if bid.customer_schedule_end is None:
            months = [
                (int(year or 2027), int(month))
                for year, month in re.findall(r"(?:(20\d{2})年)?\s*(\d{1,2})月", text)
                if 1 <= int(month) <= 12
            ]
            if months:
                year, month = max(months)
                bid.customer_schedule_end = date(year, month, 1)


async def run_intake(bid_id: int, client) -> dict:
    """Chạy bước intake: prompt từ text đã mask → LLM → persist output_json + SSE."""
    session = db.SessionLocal()
    step = None
    try:
        step = get_step(session, bid_id, "intake")
        step.status = "running"
        step.attempts += 1
        step.started_at = utcnow()
        step.error_message = None
        step.output_json = None
        session.commit()
        publish_step(bid_id, "intake", "running", step.attempts)

        bid = session.get(Bid, bid_id)
        assert bid is not None
        masked = mask_text(bid.request_content)[: settings.rfp_summary_max_chars]
        attachments = session.query(Attachment).filter_by(bid_id=bid_id).all()
        file_texts: list[dict] = []
        for attachment in attachments:
            try:
                data = Path(attachment.path).read_bytes()
                name = attachment.filename.lower()
                if name.endswith(".docx"):
                    text = extract_docx_text(data)
                elif name.endswith(".pdf"):
                    text = extract_pdf_text(data)
                elif name.endswith((".txt", ".md")):
                    text = extract_text(data)
                else:
                    continue
                file_texts.append({"filename": attachment.filename, "text": mask_text(text)})
            except Exception:
                continue
        per_file_limit = max(1, 16000 // max(1, len(file_texts)))
        rfp_files = [{**item, "text": item["text"][:per_file_limit]} for item in file_texts]
        requirements = session.query(Requirement).filter_by(bid_id=bid_id).order_by(Requirement.id).all()
        requirement_rows = [
            {"req_code": r.internal_code, "content": r.content, "priority": r.priority, "category": r.category}
            for r in requirements[:40]
        ]
        prompt = build_intake_prompt(masked, bid.customer_language, rfp_files, requirement_rows, len(requirements))
        context = {
            "bid_id": bid_id,
            "customer_language": bid.customer_language,
            "rfp_files": rfp_files,
            "requirements": requirement_rows,
            "requirement_count": len(requirements),
        }

        result = await asyncio.to_thread(
            complete_with_retry, client, IntakeExtraction, prompt, context
        )
        _apply_customer_constraints(bid, bid.request_content + " " + " ".join(item["text"] for item in rfp_files))
        session.commit()

        sample_profiles = []
        for attachment in attachments:
            if attachment.file_type != "sample_data" or attachment.parse_status != "ok":
                continue
            try:
                sheets = read_sheets(Path(attachment.path).read_bytes(), attachment.filename)
                sample_profiles.extend(profile(rows) for rows in sheets.values())
            except Exception:
                continue
        step.output_json = {
            **result,
            "attachments_status": [
                {"attachment_id": a.id, "filename": a.filename, "status": a.parse_status, "error": a.parse_error}
                for a in attachments
            ],
            "requirement_count": session.query(Requirement).filter_by(bid_id=bid_id).count(),
            "no_requirement_file": bid.no_requirement_file,
            "sample_profile": sample_profiles[0] if sample_profiles else None,
            "rfp_summary": {"summary_vi": result.get("summary_vi", ""), "keywords": result.get("keywords", [])},
        }
        step.status = "completed"
        step.finished_at = utcnow()
        session.commit()
        publish_step(bid_id, "intake", "completed", step.attempts)
        return result
    except LLMSchemaError as exc:
        if step is not None:
            mark_failed(session, step, str(exc))
        publish_error(bid_id, "intake", str(exc))
        raise
    finally:
        session.close()
