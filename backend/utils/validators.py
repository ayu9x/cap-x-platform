"""
Validators Module
Provides validation functions for user input, configurations, and data
"""

import re
from typing import Dict, Any, List, Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # RFC 5322 compliant email regex (simplified)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:
        return False, "Email is too long (max 254 characters)"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format
    
    Requirements:
    - 3-30 characters
    - Alphanumeric, underscores, and hyphens only
    - Must start with a letter
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username is too long (max 30 characters)"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"
    
    return True, None


def validate_application_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate application configuration
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['name', 'description', 'repository']
    
    # Check required fields
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
        
        if not config[field] or not str(config[field]).strip():
            return False, f"Field '{field}' cannot be empty"
    
    # Validate name
    name = config['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "Application name must contain only lowercase letters, numbers, and hyphens"
    
    if len(name) < 3 or len(name) > 50:
        return False, "Application name must be between 3 and 50 characters"
    
    # Validate repository URL
    repository = config['repository']
    if not re.match(r'^https?://', repository) and not re.match(r'^git@', repository):
        return False, "Repository must be a valid HTTP(S) or SSH Git URL"
    
    # Validate environment if provided
    if 'environment' in config:
        valid_environments = ['development', 'staging', 'production']
        if config['environment'] not in valid_environments:
            return False, f"Environment must be one of: {', '.join(valid_environments)}"
    
    return True, None


def validate_deployment_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate deployment configuration
    
    Args:
        config: Deployment configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['application_id', 'version', 'environment']
    
    # Check required fields
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    # Validate version format (semantic versioning)
    version = config['version']
    if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$', version):
        return False, "Version must follow semantic versioning (e.g., 1.0.0 or 1.0.0-beta)"
    
    # Validate environment
    valid_environments = ['development', 'staging', 'production']
    if config['environment'] not in valid_environments:
        return False, f"Environment must be one of: {', '.join(valid_environments)}"
    
    # Validate replicas if provided
    if 'replicas' in config:
        replicas = config['replicas']
        if not isinstance(replicas, int) or replicas < 1 or replicas > 100:
            return False, "Replicas must be an integer between 1 and 100"
    
    # Validate resources if provided
    if 'resources' in config:
        resources = config['resources']
        
        if 'cpu' in resources:
            cpu = resources['cpu']
            if not re.match(r'^\d+m?$', str(cpu)):
                return False, "CPU must be in format '100m' or '1' (millicores or cores)"
        
        if 'memory' in resources:
            memory = resources['memory']
            if not re.match(r'^\d+(Mi|Gi)$', str(memory)):
                return False, "Memory must be in format '256Mi' or '1Gi'"
    
    return True, None


def validate_incident_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate incident data
    
    Args:
        data: Incident data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['title', 'description', 'severity']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not data[field] or not str(data[field]).strip():
            return False, f"Field '{field}' cannot be empty"
    
    # Validate severity
    valid_severities = ['low', 'medium', 'high', 'critical']
    if data['severity'] not in valid_severities:
        return False, f"Severity must be one of: {', '.join(valid_severities)}"
    
    # Validate title length
    if len(data['title']) < 5 or len(data['title']) > 200:
        return False, "Title must be between 5 and 200 characters"
    
    # Validate description length
    if len(data['description']) < 10 or len(data['description']) > 2000:
        return False, "Description must be between 10 and 2000 characters"
    
    return True, None


def validate_pipeline_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate CI/CD pipeline configuration
    
    Args:
        config: Pipeline configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['name', 'repository', 'branch']
    
    # Check required fields
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    # Validate name
    name = config['name']
    if len(name) < 3 or len(name) > 100:
        return False, "Pipeline name must be between 3 and 100 characters"
    
    # Validate branch name
    branch = config['branch']
    if not re.match(r'^[a-zA-Z0-9/_-]+$', branch):
        return False, "Branch name contains invalid characters"
    
    # Validate stages if provided
    if 'stages' in config:
        stages = config['stages']
        if not isinstance(stages, list) or len(stages) == 0:
            return False, "Stages must be a non-empty list"
        
        for stage in stages:
            if 'name' not in stage:
                return False, "Each stage must have a name"
            if 'type' not in stage:
                return False, "Each stage must have a type"
    
    return True, None


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Convert to string and strip whitespace
    sanitized = str(input_str).strip()
    
    # Truncate to max length
    sanitized = sanitized[:max_length]
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    sanitized = ''.join(char for char in sanitized if char == '\n' or char == '\t' or ord(char) >= 32)
    
    return sanitized


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate data against a simple JSON schema
    
    Args:
        data: Data to validate
        schema: Schema definition
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    for field, field_type in schema.items():
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not isinstance(data[field], field_type):
            return False, f"Field '{field}' must be of type {field_type.__name__}"
    
    return True, None


def validate_port(port: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate port number
    
    Args:
        port: Port number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return False, "Port must be between 1 and 65535"
        return True, None
    except (ValueError, TypeError):
        return False, "Port must be a valid integer"


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"
    
    url_pattern = r'^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$'
    
    if not re.match(url_pattern, url):
        return False, "Invalid URL format"
    
    return True, None


def validate_ip_address(ip: str) -> Tuple[bool, Optional[str]]:
    """
    Validate IPv4 address
    
    Args:
        ip: IP address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ip:
        return False, "IP address is required"
    
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if not re.match(ip_pattern, ip):
        return False, "Invalid IP address format"
    
    # Validate each octet
    octets = ip.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False, "IP address octets must be between 0 and 255"
    
    return True, None
