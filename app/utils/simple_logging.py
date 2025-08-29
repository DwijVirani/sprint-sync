import logging
import sys
import json
from typing import Any, Dict
from datetime import datetime
import traceback


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "sprintsync-api",
            "version": "1.0.0",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup structured logging configuration."""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Create application logger
    app_logger = logging.getLogger("sprintsync")
    
    return app_logger


def log_exception(exc: Exception, context: Dict[str, Any] = None, logger_name: str = "sprintsync") -> None:
    """Log an exception with full stack trace and context."""
    logger = logging.getLogger(logger_name)
    
    extra_context = {
        "event": "exception_occurred",
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
    }
    
    if context:
        extra_context.update(context)
    
    logger.error("Exception occurred", exc_info=exc, extra=extra_context)


def get_request_logger(request_id: str = None, user_id: str = None) -> logging.Logger:
    """Get a logger with request-specific context."""
    logger = logging.getLogger("sprintsync.request")
    
    # Create a custom LoggerAdapter to add context to all log calls
    class RequestLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            extra = kwargs.get('extra', {})
            if request_id:
                extra['request_id'] = request_id
            if user_id:
                extra['user_id'] = user_id
            kwargs['extra'] = extra
            return msg, kwargs
    
    return RequestLoggerAdapter(logger, {})
