import sys
import logging
import structlog
from typing import Any, Dict
import json
import traceback
from datetime import datetime


class StructuredLogger:
    """Structured logger configuration for the application."""
    
    def __init__(self):
        self._configure_structlog()
    
    def _configure_structlog(self):
        """Configure structlog with JSON output and standard fields."""
        
        def add_timestamp(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
            """Add timestamp to log records."""
            event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
            return event_dict
        
        def add_service_context(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
            """Add service context to log records."""
            event_dict["service"] = "sprintsync-api"
            event_dict["version"] = "1.0.0"
            return event_dict
        
        # Configure structlog
        structlog.configure(
            processors=[
                # Filter out debug logs in production
                structlog.stdlib.filter_by_level,
                # Add timestamp and service context
                add_timestamp,
                add_service_context,
                # Add log level and logger name
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                # Position positional arguments
                structlog.stdlib.PositionalArgumentsFormatter(),
                # Process stack info
                structlog.processors.StackInfoRenderer(),
                # Format exceptions
                structlog.processors.format_exc_info,
                # Add extra context from calls
                structlog.processors.CallsiteParameterAdder(
                    parameters=[structlog.processors.CallsiteParameter.FILENAME,
                              structlog.processors.CallsiteParameter.FUNC_NAME,
                              structlog.processors.CallsiteParameter.LINENO]
                ),
                # Convert to JSON
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            context_class=dict,
            cache_logger_on_first_use=True,
        )
        
        # Configure standard library logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )
    
    def get_logger(self, name: str = "sprintsync") -> structlog.stdlib.BoundLogger:
        """Get a structured logger instance."""
        return structlog.get_logger(name)


# Global logger instance
structured_logger = StructuredLogger()
logger = structured_logger.get_logger()


def log_exception(exc: Exception, context: Dict[str, Any] = None) -> None:
    """Log an exception with full stack trace and context."""
    error_context = {
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
        "stack_trace": traceback.format_exception(type(exc), exc, exc.__traceback__)
    }
    
    if context:
        error_context.update(context)
    
    logger.error("Exception occurred", **error_context)


def get_request_logger(request_id: str = None) -> structlog.stdlib.BoundLogger:
    """Get a logger with request-specific context."""
    context = {}
    if request_id:
        context["request_id"] = request_id
    
    return logger.bind(**context)
