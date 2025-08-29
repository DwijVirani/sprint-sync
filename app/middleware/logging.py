import time
import uuid
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import traceback
import json

from app.utils.simple_logging import get_request_logger, log_exception
from app.utils.auth_utils import extract_user_id_from_request
import logging


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of API requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Get request start time
        start_time = time.time()
        
        # Extract user ID from request (you'll need to implement this based on your auth system)
        user_id = await extract_user_id_from_request(request)
        
        # Get request logger with context
        request_logger = get_request_logger(request_id)
        
        # Log request start
        request_context = {
            "event": "request_started",
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent"),
            "client_ip": self._get_client_ip(request),
            "user_id": user_id,
            "request_id": request_id
        }
        
        request_logger.info("API request started", extra=request_context)
        
        response = None
        status_code = 500
        error_occurred = False
        
        try:
            # Process the request
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as exc:
            error_occurred = True
            status_code = 500
            
            # Log the exception with full context
            error_context = {
                "event": "request_error",
                "method": request.method,
                "path": str(request.url.path),
                "user_id": user_id,
                "request_id": request_id,
                "error_type": exc.__class__.__name__,
                "error_message": str(exc),
                "stack_trace": traceback.format_exception(type(exc), exc, exc.__traceback__)
            }
            
            request_logger.error("API request failed with exception", exc_info=exc, extra=error_context)
            
            # Return error response
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "timestamp": time.time()
                }
            )
        
        finally:
            # Calculate latency
            end_time = time.time()
            latency_ms = round((end_time - start_time) * 1000, 2)
            
            # Log request completion
            completion_context = {
                "event": "request_completed",
                "method": request.method,
                "path": str(request.url.path),
                "status_code": status_code,
                "latency_ms": latency_ms,
                "user_id": user_id,
                "request_id": request_id,
                "error_occurred": error_occurred
            }
            
            if error_occurred:
                request_logger.error("API request completed with error", extra=completion_context)
            else:
                request_logger.info("API request completed successfully", extra=completion_context)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first (for reverse proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
