import os
import re
import shutil
import subprocess
import tempfile

_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff00-\uffef]")
_TTF_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
)


def _register_fonts() -> tuple[str, str]:
    """Return (latin_font, cjk_font): a Unicode TTF when available, built-in CID font for Japanese."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont

    latin = "Helvetica"
    for path in _TTF_CANDIDATES:
        if os.path.isfile(path):
            try:
                pdfmetrics.registerFont(TTFont("ExportSans", path))
                latin = "ExportSans"
                break
            except Exception:  # noqa: BLE001 - unreadable font file, try the next one
                continue
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    return latin, "HeiseiKakuGo-W5"


def _fallback_pdf(docx_bytes: bytes) -> bytes:
    from io import BytesIO
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph as DocxParagraph
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table as PdfTable, TableStyle
    from xml.sax.saxutils import escape

    latin, cjk = _register_fonts()
    base = getSampleStyleSheet()
    styles = {
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=10, leading=14),
        "title": ParagraphStyle("title", parent=base["Title"], fontSize=22, leading=28),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontSize=15, leading=19, textColor=colors.HexColor("#1F3A5F")),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=12, leading=16, textColor=colors.HexColor("#1F3A5F")),
        "cell": ParagraphStyle("cell", parent=base["BodyText"], fontSize=8, leading=10),
    }

    def para(text: str, style_key: str, bullet: bool = False):
        style = styles[style_key]
        font = cjk if _CJK.search(text) else latin
        style = ParagraphStyle(f"{style_key}-{font}", parent=style, fontName=font, leftIndent=10 if bullet else 0)
        return Paragraph(("• " if bullet else "") + escape(text), style)

    document = Document(BytesIO(docx_bytes))
    story = []
    for child in document.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            paragraph = DocxParagraph(child, document)
            if any(br.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type") == "page" for br in child.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br")):
                story.append(PageBreak())
            text = paragraph.text.strip()
            if not text:
                continue
            style_name = paragraph.style.name if paragraph.style is not None else ""
            key = {"Title": "title", "Heading 1": "h1", "Heading 2": "h2"}.get(style_name, "body")
            for line in text.split("\n"):
                story.append(para(line, key, bullet=style_name == "List Bullet"))
            story.append(Spacer(1, 2 * mm))
        elif tag == "tbl":
            table = Table(child, document)
            rows = [[para(cell.text, "cell") for cell in row.cells] for row in table.rows]
            if rows:
                pdf_table = PdfTable(rows, repeatRows=1)
                pdf_table.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.extend([pdf_table, Spacer(1, 4 * mm)])
    output = BytesIO()
    SimpleDocTemplate(output, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, invariant=1).build(story)
    return output.getvalue()


def docx_to_pdf(docx_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "proposal.docx"); open(src, "wb").write(docx_bytes)
        try:
            executable = shutil.which("libreoffice") or shutil.which("soffice")
            if not executable:
                return _fallback_pdf(docx_bytes)
            # Keep LibreOffice's profile inside the request temp directory. This
            # avoids profile-lock and permission failures in the preview container.
            profile = os.path.join(d, "lo-profile")
            subprocess.run([
                executable,
                "--headless",
                f"-env:UserInstallation=file://{profile}",
                "--convert-to", "pdf",
                "--outdir", d,
                src,
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = os.path.join(d, "proposal.pdf")
            if not os.path.isfile(output):
                raise OSError("LibreOffice did not produce proposal.pdf")
            return open(output, "rb").read()
        except (OSError, subprocess.CalledProcessError):
            return _fallback_pdf(docx_bytes)
