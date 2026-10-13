"""Envelope lỗi chuẩn — contract api_contract.md §1.3.

Mọi lỗi trả về:
    {"error": {"code": "...", "message": "<tiếng Việt>", "details": {...}}}
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """Lỗi nghiệp vụ với envelope chuẩn — handler đăng ký trong main.py."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


def not_found(message: str = "Không tìm thấy hồ sơ") -> ApiError:
    return ApiError(404, "NOT_FOUND", message)


def validation_error(message: str, details: dict[str, Any] | None = None) -> ApiError:
    return ApiError(400, "VALIDATION_ERROR", message, details)


def state_conflict(message: str, details: dict[str, Any] | None = None) -> ApiError:
    return ApiError(409, "STATE_CONFLICT", message, details)


def clarify_pending(message: str, details: dict[str, Any] | None = None) -> ApiError:
    return ApiError(409, "CLARIFY_PENDING", message, details)


def pipeline_error(message: str, details: dict[str, Any] | None = None) -> ApiError:
    return ApiError(422, "PIPELINE_ERROR", message, details)

def check_failed(message: str, details: dict[str, Any] | None = None) -> ApiError:
    return ApiError(422, "CHECK_FAILED", message, details)


async def api_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ApiError)
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    """Biến lỗi validate của FastAPI (mặc định 422) thành 400 VALIDATION_ERROR.

    ``request_content`` ngắn hơn 30 ký tự → ``details.min_length=30`` (FR-001.1).
    """
    details: dict[str, Any] = {}
    errors: list[dict[str, Any]] = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err.get("loc", []) if part != "body")
        errors.append({"field": loc, "message": err.get("msg", "")})
        if err.get("type") == "string_too_short" and loc == "request_content":
            details["min_length"] = err.get("ctx", {}).get("min_length")

    details["errors"] = errors
    message = "Dữ liệu gửi lên không hợp lệ"
    if "min_length" in details:
        message = "Nội dung yêu cầu phải có ít nhất 30 ký tự"
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "VALIDATION_ERROR", "message": message, "details": details}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
