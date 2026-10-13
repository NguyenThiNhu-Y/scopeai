import os
import shutil
import subprocess
import tempfile


def _fallback_pdf(docx_bytes: bytes) -> bytes:
    from io import BytesIO
    from docx import Document
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from xml.sax.saxutils import escape

    document = Document(BytesIO(docx_bytes))
    styles = getSampleStyleSheet()
    story = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            story.append(Paragraph(escape(text), styles["BodyText"]))
            story.append(Spacer(1, 3 * mm))
    output = BytesIO()
    SimpleDocTemplate(output, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm).build(story)
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
