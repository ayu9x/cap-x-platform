"""
Backend Utilities Package
Provides utility functions, validators, middleware, and logging configuration
"""

from .validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_deployment_config,
    validate_application_config,
    sanitize_input
)

from .auth_middleware import (
    token_required,
    admin_required,
    generate_token,
    verify_token,
    hash_password,
    verify_password
)

from .logger import (
    setup_logger,
    get_logger,
    log_request,
    log_response,
    log_error
)

__all__ = [
    # Validators
    'validate_email',
    'validate_password',
    'validate_username',
    'validate_deployment_config',
    'validate_application_config',
    'sanitize_input',
    
    # Auth
    'token_required',
    'admin_required',
    'generate_token',
    'verify_token',
    'hash_password',
    'verify_password',
    
    # Logger
    'setup_logger',
    'get_logger',
    'log_request',
    'log_response',
    'log_error'
]
