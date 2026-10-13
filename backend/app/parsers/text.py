def extract_text(data: bytes) -> str:
    try: return data.decode("utf-8")
    except UnicodeDecodeError as exc: raise ValueError("Không đọc được văn bản — hãy lưu file UTF-8") from exc
