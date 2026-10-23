# app/core/errors.py
"""RFC-7807 Problem Details compliant error handling."""

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional


class ProblemDetail(BaseModel):
    """RFC-7807 standard problem details schema."""
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    invalid_params: Optional[list] = None


class AppException(Exception):
    """Custom application exception conforming to RFC-7807."""

    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        error_type: str = "about:blank",
        invalid_params: Optional[list] = None
    ):
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.error_type = error_type
        self.invalid_params = invalid_params
        super().__init__(detail)


def create_problem_response(
    status_code: int,
    title: str,
    detail: str,
    instance: Optional[str] = None,
    error_type: str = "about:blank",
    invalid_params: Optional[list] = None
) -> JSONResponse:
    """Create an RFC-7807 compliant JSONResponse."""
    payload = {
        "type": error_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance
    }
    if invalid_params:
        payload["invalid_params"] = invalid_params

    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json"
    )


async def app_exception_handler(
        request: Request, exc: AppException) -> JSONResponse:
    """FastAPI global exception handler for AppException."""
    return create_problem_response(
        status_code=exc.status_code,
        title=exc.title,
        detail=exc.detail,
        instance=request.url.path,
        error_type=exc.error_type,
        invalid_params=exc.invalid_params
    )
