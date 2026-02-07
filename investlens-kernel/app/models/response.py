"""
API Response Models
===================

Standardized response format for all API endpoints.
Provides consistent structure: {code, message, data, trace_id}
"""

from typing import Any, Optional, Generic, TypeVar
# pyre-ignore[21]: pydantic installed but not found
from pydantic import BaseModel, Field
from uuid import uuid4

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """
    Unified API Response Format
    ---------------------------
    All API endpoints should return this structure for consistency.
    
    Attributes:
        code: HTTP-like status code (200, 400, 404, 500, 502)
        message: Human-readable status message
        data: The actual response payload (generic type)
        trace_id: Unique identifier for request tracing
    """
    code: int = Field(default=200, description="Status code")
    message: str = Field(default="success", description="Status message")
    data: Optional[T] = Field(default=None, description="Response payload")
    trace_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique request trace ID"
    )


class ErrorResponse(BaseModel):
    """
    Standard Error Response
    -----------------------
    Used for error responses with additional details.
    """
    code: int
    message: str
    detail: Optional[str] = None
    trace_id: str = Field(default_factory=lambda: str(uuid4()))


# Convenience functions for creating responses
def success_response(
    data: Any = None,
    message: str = "success",
    trace_id: Optional[str] = None
) -> dict:
    """Create a success response dict."""
    return {
        "code": 200,
        "message": message,
        "data": data,
        "trace_id": trace_id or str(uuid4())
    }


def error_response(
    code: int,
    message: str,
    detail: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict:
    """Create an error response dict."""
    return {
        "code": code,
        "message": message,
        "detail": detail,
        "trace_id": trace_id or str(uuid4())
    }


# Common error responses
def bad_request(
    message: str = "Bad request",
    detail: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict:
    """400 Bad Request"""
    return error_response(400, message, detail, trace_id)


def not_found(
    message: str = "Not found",
    detail: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict:
    """404 Not Found"""
    return error_response(404, message, detail, trace_id)


def internal_error(
    message: str = "Internal server error",
    detail: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict:
    """500 Internal Server Error"""
    return error_response(500, message, detail, trace_id)


def upstream_error(
    message: str = "Upstream service error",
    detail: Optional[str] = None,
    trace_id: Optional[str] = None
) -> dict:
    """502 Bad Gateway - for external API failures"""
    return error_response(502, message, detail, trace_id)
