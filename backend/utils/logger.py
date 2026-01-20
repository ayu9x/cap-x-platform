"""
Logger Module
Provides structured logging configuration and utilities
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors
        
        Args:
            record: Log record to format
            
        Returns:
            Colored log string
        """
        # Get color for log level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format log message
        log_msg = f"{color}[{timestamp}] {record.levelname:8s}{reset} - {record.name} - {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            log_msg += f"\n{self.formatException(record.exc_info)}"
        
        return log_msg


def setup_logger(
    name: str,
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    json_format: bool = False,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        json_format: Use JSON formatting for file logs
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if log file specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Use JSON or standard formatter
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_request(logger: logging.Logger, request: Any) -> None:
    """
    Log HTTP request details
    
    Args:
        logger: Logger instance
        request: Flask request object
    """
    logger.info(
        f"Request: {request.method} {request.path}",
        extra={
            'extra_data': {
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            }
        }
    )


def log_response(logger: logging.Logger, request: Any, response: Any, 
                duration_ms: Optional[float] = None) -> None:
    """
    Log HTTP response details
    
    Args:
        logger: Logger instance
        request: Flask request object
        response: Flask response object
        duration_ms: Request duration in milliseconds
    """
    extra_data = {
        'method': request.method,
        'path': request.path,
        'status_code': response.status_code
    }
    
    if duration_ms is not None:
        extra_data['duration_ms'] = duration_ms
    
    logger.info(
        f"Response: {request.method} {request.path} - {response.status_code}",
        extra={'extra_data': extra_data}
    )


def log_error(logger: logging.Logger, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log error with context
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Additional context information
    """
    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error)
    }
    
    if context:
        error_data['context'] = context
    
    logger.error(
        f"Error: {type(error).__name__} - {str(error)}",
        exc_info=True,
        extra={'extra_data': error_data}
    )


def log_audit(logger: logging.Logger, user_id: str, action: str, 
             resource: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log audit trail for user actions
    
    Args:
        logger: Logger instance
        user_id: User ID performing the action
        action: Action performed
        resource: Resource affected
        details: Additional details
    """
    audit_data = {
        'user_id': user_id,
        'action': action,
        'resource': resource,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        audit_data['details'] = details
    
    logger.info(
        f"Audit: {user_id} - {action} - {resource}",
        extra={'extra_data': audit_data}
    )


def log_performance(logger: logging.Logger, operation: str, 
                   duration_ms: float, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        metadata: Additional metadata
    """
    perf_data = {
        'operation': operation,
        'duration_ms': duration_ms,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if metadata:
        perf_data['metadata'] = metadata
    
    # Log as warning if operation is slow (>1000ms)
    if duration_ms > 1000:
        logger.warning(
            f"Slow operation: {operation} took {duration_ms:.2f}ms",
            extra={'extra_data': perf_data}
        )
    else:
        logger.debug(
            f"Performance: {operation} took {duration_ms:.2f}ms",
            extra={'extra_data': perf_data}
        )


def log_security_event(logger: logging.Logger, event_type: str, 
                       severity: str, details: Dict[str, Any]) -> None:
    """
    Log security-related events
    
    Args:
        logger: Logger instance
        event_type: Type of security event
        severity: Severity level (low, medium, high, critical)
        details: Event details
    """
    security_data = {
        'event_type': event_type,
        'severity': severity,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details
    }
    
    # Map severity to log level
    severity_map = {
        'low': logging.INFO,
        'medium': logging.WARNING,
        'high': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    log_level = severity_map.get(severity.lower(), logging.WARNING)
    
    logger.log(
        log_level,
        f"Security Event: {event_type} - {severity}",
        extra={'extra_data': security_data}
    )


class RequestLogger:
    """Context manager for logging request/response with timing"""
    
    def __init__(self, logger: logging.Logger, request: Any):
        """
        Initialize request logger
        
        Args:
            logger: Logger instance
            request: Flask request object
        """
        self.logger = logger
        self.request = request
        self.start_time = None
    
    def __enter__(self):
        """Start timing and log request"""
        self.start_time = datetime.utcnow()
        log_request(self.logger, self.request)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log response with duration"""
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
            
            if exc_type:
                log_error(self.logger, exc_val, {
                    'method': self.request.method,
                    'path': self.request.path,
                    'duration_ms': duration
                })
            else:
                self.logger.info(
                    f"Request completed: {self.request.method} {self.request.path} - {duration:.2f}ms",
                    extra={'extra_data': {
                        'method': self.request.method,
                        'path': self.request.path,
                        'duration_ms': duration
                    }}
                )


# Create default application logger
app_logger = setup_logger(
    'capx',
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_file=os.getenv('LOG_FILE', 'logs/capx.log'),
    json_format=os.getenv('LOG_JSON', 'false').lower() == 'true'
)
