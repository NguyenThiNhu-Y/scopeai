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


def _apply_customer_constraints(bid: Bid, text: str) -> None:
    """Persist explicit RFP budget and milestones; never delegate numbers to LLM."""
    budget = re.search(r"1,500万円|1500万円", text)
    if budget:
        bid.budget_amount = 15_000_000
        bid.budget_currency = "JPY"

    # Mốc khách: bắt đầu / MVP / Production (RFP Nhật: 2027/1, 2027/6, 2027/9).
    start = _find_milestone(text, ("着手", "開始", "スタート", "起動"))
    mvp = _find_milestone(text, ("MVP",))
    production = _find_milestone(text, ("本番", "production", "正式稼働"))
    if start:
        bid.customer_schedule_start = start
    if mvp:
        bid.customer_mvp_start = mvp
    if production:
        bid.customer_production_start = production
        bid.customer_schedule_end = production
    else:
        # Fallback: tháng lớn nhất xuất hiện trong văn bản.
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
