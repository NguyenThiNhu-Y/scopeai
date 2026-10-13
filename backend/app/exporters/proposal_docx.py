from io import BytesIO
from docx import Document
from docx.shared import Pt


def render_proposal(data: dict) -> bytes:
    d = Document(); d.core_properties.title = data["project_name"]
    d.add_heading(data["project_name"], 0); d.add_paragraph(data["customer_name"])
    d.add_page_break(); d.add_heading(data["labels"].get("toc", "Mục lục"), 1)
    toc = "\n".join(
        f"{index}. {data['labels'].get(key, key)}"
        for index, key in enumerate(data["sections"], 1)
    )
    d.add_paragraph(toc)
    for key, value in data["sections"].items():
        d.add_heading(data["labels"].get(key, key), 1); d.add_paragraph(value)
    if data.get("assumptions") or data.get("scope_out"):
        if data.get("assumptions"):
            d.add_heading(data["labels"].get("assumptions_and_scope", data["labels"].get("assumptions", "Assumptions and out of scope")), 1)
            for item in data["assumptions"]: d.add_paragraph(item, style="List Bullet")
        if data.get("scope_out"):
            d.add_heading(data["labels"].get("scope_out", "Out of scope"), 1)
            for item in data["scope_out"]: d.add_paragraph(item, style="List Bullet")
    if data.get("quotation"):
        d.add_heading(data["labels"].get("quotation", "Quotation"), 1); d.add_paragraph(data["quotation"])
    stream = BytesIO(); d.save(stream); return stream.getvalue()
