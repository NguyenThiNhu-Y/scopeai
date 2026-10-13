from io import BytesIO, StringIO
import csv

HEADER_SCAN_ROWS = 10


def _clean(value) -> str:
    return str(value).strip() if value is not None else ""


def _header_index(values: list[tuple], filename: str) -> int:
    best_index = 0
    best_score = -1
    for index, row in enumerate(values[:HEADER_SCAN_ROWS]):
        cells = {_clean(value).lower() for value in row}
        text = " ".join(cells)
        score = sum(token in text for token in ("no", "code", "要件id", "要件名", "要件内容", "対応可否", "補足説明", "requirement", "内容", "description", "nội dung"))
        if score > best_score:
            best_index = index
            best_score = score
    return best_index


def read_sheets(data: bytes, filename: str) -> dict[str, list[dict]]:
    if filename.lower().endswith(".xls"):
        from app.parsers.xls import read_sheets as read_legacy
        return read_legacy(data, filename)
    if filename.lower().endswith(".csv"):
        values = [tuple(row) for row in csv.reader(StringIO(data.decode("utf-8-sig")))]
        header_row = _header_index(values, filename)
        if not values:
            return {"CSV": []}
        headers = [_clean(v) or f"column_{i + 1}" for i, v in enumerate(values[header_row])]
        rows = []
        for row_number, values_row in enumerate(values[header_row + 1:], header_row + 2):
            if any(_clean(v) for v in values_row):
                row = dict(zip(headers, values_row))
                row["__header_row__"] = str(header_row + 1)
                row["__row__"] = str(row_number)
                rows.append(row)
        return {"CSV": rows}
    try:
        import openpyxl
        wb = openpyxl.load_workbook(BytesIO(data), data_only=False, read_only=True)
        out = {}
        for ws in wb.worksheets:
            values = list(ws.values)
            if not values: continue
            header_row = _header_index(values, filename)
            headers = [_clean(v) or f"column_{i + 1}" for i, v in enumerate(values[header_row])]
            rows = []
            for row_number, row in enumerate(values[header_row + 1:], header_row + 2):
                if any(v is not None for v in row):
                    item = dict(zip(headers, row))
                    item["__row__"] = row_number
                    item["__header_row__"] = header_row + 1
                    rows.append(item)
            out[ws.title] = rows
        return out
    except Exception as exc: raise ValueError("Không đọc được Excel — hãy kiểm tra workbook và mapping cột") from exc
