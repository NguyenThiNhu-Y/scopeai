"""Service case study — template, import, file WBS (thiet_ke_danh_gia.md §3).

- ``build_template_xlsx``: file Excel mẫu để nhập case study (1 dòng = 1 case).
- ``import_cases``: đọc .xlsx/.csv/.yaml, preview (lỗi theo dòng) hoặc save
  (gộp theo id, che PII, tạo phiên bản settings mới + changelog).
- ``upload_wbs`` / ``download_wbs``: file WBS Excel của dự án cũ theo case;
  đọc sheet WBS, kiểm tổng thực tế khớp ``actual_man_day``, tính điểm nóng.

Mọi số liệu đều là dữ liệu giả lập; không gọi LLM.
"""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any

import yaml

from app.api.errors import not_found, validation_error
from app.models import ReferenceSetting
from app.privacy import mask_text
from app.schemas.case_study import normalize_case_studies
from app.services import settings_service
from app.services.reference_service import ROOT

# Thư mục file WBS mặc định (bộ mẫu) và file WBS do người dùng tải lên.
REFERENCE_WBS_DIR = ROOT / "reference" / "case_studies_wbs"
DATA_ROOT = Path("data/case_studies")

# Cột phẳng trong Excel/CSV mẫu → trường schema (trường lồng tách cột).
_DIRECT_FIELDS = (
    "id",
    "title",
    "industry",
    "market",
    "customer_language",
    "direction",
    "requirement_count",
    "year",
    "public",
    "summary",
    "wbs_file",
)
_LIST_FIELDS = ("factors", "tech", "lessons_vi")
_NESTED_PREFIXES = {
    "estimated_": "estimated_man_day",
    "actual_": "actual_man_day",
    "duration_": "actual_duration_weeks",
    "team_": "team_peak",
}
_PHASE_ALIASES = {
    "poc": "poc",
    "mvp": "mvp",
    "production": "production",
    "prod": "production",
    "本開発": "production",
}


# ---------------------------------------------------------------- helpers

def _current_cases(session) -> list[dict]:
    """Danh sách case study hiện tại (DB override nếu có, nếu không lấy mặc định)."""
    row = session.get(ReferenceSetting, "case_studies")
    if row is not None:
        return list(row.payload or [])
    return list(settings_service._repo_payload("case_studies"))


def _find_case(cases: list[dict], case_id: str) -> dict:
    for case in cases:
        if case.get("id") == case_id:
            return case
    raise not_found(f"Không tìm thấy case study '{case_id}'")


def _split_list(value: Any) -> list[str]:
    """Tách chuỗi 'a, b / dòng mới' thành list; trả nguyên list nếu đã là list."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    parts = text.replace("\n", ",").split(",")
    return [part.strip() for part in parts if part.strip()]


def _unflatten_row(row: dict) -> dict:
    """Map dòng Excel/CSV (cột phẳng) thành dict lồng theo schema case study.

    Ô trống (None/'') được bỏ qua — trường tùy chọn không bị đặt giá trị rỗng.
    """
    case: dict[str, Any] = {}
    for key, value in row.items():
        if key.startswith("__"):
            continue
        name = str(key).strip()
        if not name:
            continue
        if value is None or str(value).strip() == "":
            continue
        if name in _DIRECT_FIELDS:
            case[name] = value
        elif name in _LIST_FIELDS:
            case[name] = _split_list(value)
        elif name in ("win_reason_vi", "lost_reason_vi"):
            case.setdefault("bid_outcome", {})[name] = value
        elif name == "bid_month":
            # Trường schema là bid_outcome.bid_month (không phải bid_outcome.month).
            case.setdefault("bid_outcome", {})["bid_month"] = value
        elif name.startswith("bid_"):
            case.setdefault("bid_outcome", {})[name[len("bid_"):]] = value
        elif name.startswith("contract_"):
            case.setdefault("bid_outcome", {}).setdefault("contract_model", {})[
                name[len("contract_"):]
            ] = value
        else:
            for prefix, nested in _NESTED_PREFIXES.items():
                if name.startswith(prefix):
                    case.setdefault(nested, {})[name[len(prefix):]] = value
                    break
    return case


# ---------------------------------------------------------------- template

TEMPLATE_COLUMNS = [
    "id", "title", "industry", "market", "customer_language", "direction",
    "requirement_count", "year", "public", "summary",
    "factors", "tech", "lessons_vi",
    "estimated_poc", "estimated_mvp", "estimated_production",
    "actual_poc", "actual_mvp", "actual_production",
    "duration_poc", "duration_go_no_go", "duration_mvp", "duration_production",
    "team_pm", "team_ba", "team_brse", "team_ai_engineer", "team_backend",
    "team_frontend", "team_qa", "team_infra",
    "bid_result", "bid_month", "contract_poc", "contract_mvp", "contract_production",
    "win_reason_vi", "lost_reason_vi", "wbs_file",
]


def _flatten_case(case: dict) -> dict:
    """Chuyển case dict lồng thành dòng cột phẳng cho Excel mẫu."""
    flat: dict[str, Any] = {}
    for field in _DIRECT_FIELDS:
        flat[field] = case.get(field)
    for field in _LIST_FIELDS:
        flat[field] = ", ".join(case.get(field) or [])
    for prefix, nested in _NESTED_PREFIXES.items():
        for sub, value in (case.get(nested) or {}).items():
            flat[f"{prefix}{sub}"] = value
    bid = case.get("bid_outcome") or {}
    flat["bid_result"] = bid.get("result")
    flat["bid_month"] = bid.get("bid_month")
    for sub, value in (bid.get("contract_model") or {}).items():
        flat[f"contract_{sub}"] = value
    flat["win_reason_vi"] = bid.get("win_reason_vi")
    flat["lost_reason_vi"] = bid.get("lost_reason_vi")
    return flat


def build_template_xlsx() -> bytes:
    """Excel mẫu: dòng 1 = tiêu đề cột, dòng 2 = ví dụ (case đầy đủ trường).

    Dùng case có đủ trường lồng (tech, bid_outcome, wbs_file, team_peak đủ vai
    trò) để người dùng thấy định dạng đầy đủ.
    """
    from openpyxl import Workbook

    cases = settings_service._repo_payload("case_studies")
    example = next(
        (case for case in cases if case.get("bid_outcome") and case.get("wbs_file")),
        cases[0] if cases else {},
    )
    wb = Workbook()
    ws = wb.active
    ws.title = "Case studies"
    ws.append(TEMPLATE_COLUMNS)
    if example:
        flat = _flatten_case(example)
        ws.append([flat.get(col) for col in TEMPLATE_COLUMNS])
    output = BytesIO()
    wb.save(output)
    return output.getvalue()


# ---------------------------------------------------------------- import

def _read_import_rows(filename: str, data: bytes) -> list[dict]:
    """Đọc file import → list row dict (kèm ``__row__`` để báo lỗi theo dòng)."""
    name = filename.lower()
    if name.endswith((".yaml", ".yml")):
        try:
            payload = yaml.safe_load(data.decode("utf-8"))
        except yaml.YAMLError as exc:
            raise validation_error("YAML không hợp lệ", {"errors": [str(exc)]}) from exc
        if not isinstance(payload, list):
            raise validation_error("File YAML case study phải là danh sách", {"errors": ["root"]})
        # Không thêm __row__ vào dict — normalize_case_studies tự đánh số dòng.
        return [item if isinstance(item, dict) else {} for item in payload]
    if name.endswith(".csv"):
        reader = csv.DictReader(StringIO(data.decode("utf-8-sig")))
        rows = []
        for index, row in enumerate(reader, start=2):
            row = {key.strip(): value for key, value in row.items() if key is not None}
            row["__row__"] = index
            rows.append(row)
        return rows
    if name.endswith((".xlsx", ".xlsm", ".xls")):
        from app.parsers.excel import read_sheets

        sheets = read_sheets(data, filename)
        if not sheets:
            raise validation_error("File Excel không có dữ liệu")
        first = next(iter(sheets.values()))
        return first
    raise validation_error(
        "Chỉ hỗ trợ file .xlsx, .csv hoặc .yaml",
        {"errors": ["filename"]},
    )


def import_cases(session, filename: str, data: bytes, mode: str, by: str) -> dict:
    """Import case study — ``mode=preview`` (không lưu) hoặc ``mode=save``.

    - Lỗi theo từng dòng (số dòng, cột, lý do) — không chặn các dòng khác.
    - ``save``: gộp theo ``id`` (trùng ghi đè), che PII, tạo phiên bản mới.
    """
    if mode not in ("preview", "save"):
        raise validation_error("mode phải là 'preview' hoặc 'save'", {"errors": ["mode"]})
    rows = _read_import_rows(filename, data)
    structured = [
        row if filename.lower().endswith((".yaml", ".yml")) else _unflatten_row(row)
        for row in rows
    ]
    valid, errors = normalize_case_studies(structured)
    # Che PII trong summary và lessons_vi (BR-06) trước khi lưu/hiển thị.
    for case in valid:
        case["summary"] = mask_text(str(case.get("summary") or ""))
        case["lessons_vi"] = [
            mask_text(str(item)) for item in (case.get("lessons_vi") or [])
        ]

    if mode == "preview":
        return {
            "mode": "preview",
            "total": len(rows),
            "valid_count": len(valid),
            "error_count": len(errors),
            "valid": valid,
            "errors": errors,
        }

    merged = _current_cases(session)
    by_id = {case["id"]: case for case in merged}
    for case in valid:
        by_id[case["id"]] = case
    merged = [by_id[key] for key in sorted(by_id)]
    version = settings_service.update_setting(
        session,
        "case_studies",
        yaml.safe_dump(merged, allow_unicode=True, sort_keys=False),
        by,
    )["version"]
    return {
        "mode": "save",
        "total": len(rows),
        "valid_count": len(valid),
        "error_count": len(errors),
        "saved": len(valid),
        "version": version,
        "errors": errors,
    }


# ---------------------------------------------------------------- WBS file

def _normalize_phase(raw: Any) -> str | None:
    text = str(raw or "").strip().lower()
    for alias, phase in _PHASE_ALIASES.items():
        if alias in text:
            return phase
    return None


def parse_wbs_workbook(data: bytes) -> dict:
    """Đọc sheet 'WBS' của file Excel dự án cũ (định dạng bộ mẫu Tokai).

    Cột: Mã, Hạng mục (VI), 作業項目 (JA), Giai đoạn, Vai trò,
    Man-day ước lượng, Man-day thực tế, Chênh lệch, Requirement liên quan, Ghi chú.
    Mã 3 cấp ``1`` / ``1.1`` / ``1.1.01``; task lá có man-day.

    Trả về tổng thực tế theo giai đoạn, danh sách điểm nóng (thực tế vượt
    ước lượng > 30%) và cảnh báo.
    """
    import openpyxl

    try:
        wb = openpyxl.load_workbook(BytesIO(data), data_only=True)
    except Exception as exc:
        raise validation_error("Không đọc được file WBS Excel", {"errors": [str(exc)]}) from exc
    if "WBS" not in wb.sheetnames:
        raise validation_error("File WBS thiếu sheet 'WBS'", {"sheets": wb.sheetnames})
    ws = wb["WBS"]
    rows = [row for row in ws.iter_rows(values_only=True) if any(v is not None for v in row)]
    if not rows:
        raise validation_error("Sheet WBS không có dữ liệu")
    header = [str(cell or "").strip() for cell in rows[0]]

    def col_index(*aliases: str) -> int | None:
        for index, name in enumerate(header):
            if any(alias in name for alias in aliases):
                return index
        return None

    idx_code = col_index("Mã", "mã", "code")
    idx_name = col_index("Hạng mục", "作業項目", "hạng mục")
    idx_phase = col_index("Giai đoạn", "giai đoạn", "phase")
    idx_est = col_index("ước lượng", "estimate")
    idx_act = col_index("thực tế", "actual")
    idx_req = col_index("Requirement liên quan", "requirement liên quan", "requirement")
    if idx_code is None or idx_act is None:
        raise validation_error(
            "Sheet WBS thiếu cột bắt buộc (Mã, Man-day thực tế)",
            {"columns": header},
        )

    by_phase: dict[str, dict] = {
        "poc": {"estimated": 0.0, "actual": 0.0, "task_count": 0},
        "mvp": {"estimated": 0.0, "actual": 0.0, "task_count": 0},
        "production": {"estimated": 0.0, "actual": 0.0, "task_count": 0},
    }
    hotspots: list[dict] = []
    requirement_codes: set[str] = set()
    total_rows = 0
    for row in rows[1:]:
        code = str(row[idx_code] or "").strip() if idx_code < len(row) else ""
        if not code:
            continue
        phase = _normalize_phase(row[idx_phase] if idx_phase is not None and idx_phase < len(row) else None)
        if phase is None:
            continue
        estimated = _as_float(row[idx_est]) if idx_est is not None and idx_est < len(row) else None
        actual = _as_float(row[idx_act])
        if actual is None:
            continue
        total_rows += 1
        by_phase[phase]["actual"] = round(by_phase[phase]["actual"] + actual, 1)
        if estimated is not None:
            by_phase[phase]["estimated"] = round(by_phase[phase]["estimated"] + estimated, 1)
        by_phase[phase]["task_count"] += 1
        if estimated and actual > estimated * 1.3:
            hotspots.append({
                "task_code": code,
                "name_vi": str(row[idx_name] or "").strip() if idx_name is not None and idx_name < len(row) else "",
                "phase": phase,
                "estimated_man_day": estimated,
                "actual_man_day": actual,
                "ratio": round(actual / estimated, 2),
            })
        if idx_req is not None and idx_req < len(row) and row[idx_req]:
            for token in str(row[idx_req]).replace(",", " ").split():
                if token.strip():
                    requirement_codes.add(token.strip())

    return {
        "total_rows": total_rows,
        "by_phase": by_phase,
        "total_actual": round(sum(by_phase[p]["actual"] for p in by_phase), 1),
        "hotspots": hotspots,
        "requirement_codes": sorted(requirement_codes),
    }


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compare_with_actual(parse: dict, case: dict) -> list[str]:
    """Cảnh báo khi tổng man-day thực tế theo giai đoạn lệch actual_man_day > 1."""
    warnings: list[str] = []
    expected = case.get("actual_man_day") or {}
    for phase in ("poc", "mvp", "production"):
        expected_value = expected.get(phase)
        actual_value = parse["by_phase"][phase]["actual"]
        if expected_value is not None and abs(actual_value - float(expected_value)) > 1:
            warnings.append(
                f"Tổng man-day thực tế {phase} ({actual_value}) lệch quá 1 so với "
                f"actual_man_day của case ({expected_value})"
            )
    return warnings


def upload_wbs(session, case_id: str, filename: str, data: bytes, by: str) -> dict:
    """Tải file WBS lên theo case; lưu vào ``data/case_studies/<id>/``.

    Cập nhật ``wbs_file`` của case (phiên bản settings mới) và trả kết quả
    parse: tổng thực tế theo giai đoạn, điểm nóng, cảnh báo.
    """
    cases = _current_cases(session)
    case = _find_case(cases, case_id)
    if not filename.lower().endswith((".xlsx", ".xlsm")):
        raise validation_error("File WBS phải là Excel .xlsx/.xlsm", {"errors": ["filename"]})
    parse = parse_wbs_workbook(data)
    parse["warnings"] = _compare_with_actual(parse, case)

    case_dir = DATA_ROOT / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    stored_name = Path(filename).name
    (case_dir / stored_name).write_bytes(data)

    # Ghi wbs_file vào case (gộp theo id) → phiên bản settings mới + changelog.
    updated = [dict(item) for item in cases]
    for item in updated:
        if item["id"] == case_id:
            item["wbs_file"] = stored_name
    version = settings_service.update_setting(
        session,
        "case_studies",
        yaml.safe_dump(updated, allow_unicode=True, sort_keys=False),
        by,
    )["version"]
    parse["case_id"] = case_id
    parse["wbs_file"] = stored_name
    parse["version"] = version
    return parse


def resolve_wbs_file(case: dict) -> tuple[str, bytes] | None:
    """Tìm file WBS của case: ưu tiên file tải lên, sau đó file mặc định."""
    wbs_file = case.get("wbs_file")
    if not wbs_file:
        return None
    uploaded = DATA_ROOT / case["id"] / Path(wbs_file).name
    if uploaded.is_file():
        return uploaded.name, uploaded.read_bytes()
    default = REFERENCE_WBS_DIR / Path(wbs_file).name
    if default.is_file():
        return default.name, default.read_bytes()
    return None


def download_wbs(session, case_id: str) -> tuple[str, bytes]:
    """Tải file WBS của case về (file tải lên hoặc file mặc định trong reference)."""
    case = _find_case(_current_cases(session), case_id)
    resolved = resolve_wbs_file(case)
    if resolved is None:
        raise not_found(f"Case study '{case_id}' chưa có file WBS")
    return resolved