"""
Trace ID Middleware
===================

Adds unique trace_id to each request for distributed tracing and debugging.
The trace_id is accessible via request.state.trace_id in route handlers.
"""

import logging
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class TraceIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates and attaches a unique trace_id to each request.
    
    The trace_id can be:
    1. Provided by client via X-Trace-ID header (for distributed tracing)
    2. Auto-generated if not provided
    
    Access in route handlers via: request.state.trace_id
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check for existing trace_id from upstream or generate new one
        trace_id = request.headers.get("X-Trace-ID") or str(uuid4())
        
        # Attach to request state for access in route handlers
        request.state.trace_id = trace_id
        
        # Process request
        response = await call_next(request)
        
        # Add trace_id to response headers for client correlation
        response.headers["X-Trace-ID"] = trace_id
        
        return response


def get_trace_id(request: Request) -> str:
    """
    Helper function to extract trace_id from request.
    
    Usage in route handlers:
        @app.get("/api/v1/example")
        def example_endpoint(request: Request):
            trace_id = get_trace_id(request)
            return success_response(data=..., trace_id=trace_id)
    """
    return getattr(request.state, 'trace_id', str(uuid4()))
