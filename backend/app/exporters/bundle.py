from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo


def make_bundle(files: list[tuple[str, bytes]]) -> bytes:
    out = BytesIO()
    with ZipFile(out, "w", ZIP_DEFLATED) as z:
        for name, content in files:
            info = ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = ZIP_DEFLATED
            z.writestr(info, content)
    return out.getvalue()
