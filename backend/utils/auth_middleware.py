"""
Authentication Middleware
Provides JWT token management, password hashing, and authentication decorators
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Dict, Optional, Callable, Any


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def generate_token(user_id: str, email: str, role: str = 'user', 
                   expiry_hours: int = 24) -> str:
    """
    Generate JWT token for user authentication
    
    Args:
        user_id: User ID
        email: User email
        role: User role
        expiry_hours: Token expiry in hours
        
    Returns:
        JWT token string
    """
    from config import Config
    
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=expiry_hours)
    }
    
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    from config import Config
    
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def extract_token_from_header() -> Optional[str]:
    """
    Extract JWT token from Authorization header
    
    Returns:
        Token string or None if not found
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    try:
        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
    except Exception:
        pass
    
    return None


def token_required(f: Callable) -> Callable:
    """
    Decorator to require valid JWT token for route access
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': 'Access granted'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token_from_header()
        
        if not token:
            return jsonify({
                'error': 'Authentication token is missing',
                'code': 'TOKEN_MISSING'
            }), 401
        
        # Verify token
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 'TOKEN_INVALID'
            }), 401
        
        # Get user from database
        try:
            from app import db
            
            if db is None:
                return jsonify({
                    'error': 'Database connection unavailable',
                    'code': 'DB_ERROR'
                }), 500
            
            user = db.users.find_one({'_id': payload['user_id']})
            
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'code': 'USER_NOT_FOUND'
                }), 401
            
            # Pass user to route function
            return f(user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_ERROR',
                'details': str(e)
            }), 500
    
    return decorated


def admin_required(f: Callable) -> Callable:
    """
    Decorator to require admin role for route access
    
    Usage:
        @app.route('/admin')
        @admin_required
        def admin_route(current_user):
            return jsonify({'message': 'Admin access granted'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token_from_header()
        
        if not token:
            return jsonify({
                'error': 'Authentication token is missing',
                'code': 'TOKEN_MISSING'
            }), 401
        
        # Verify token
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 'TOKEN_INVALID'
            }), 401
        
        # Check admin role
        if payload.get('role') != 'admin':
            return jsonify({
                'error': 'Admin access required',
                'code': 'INSUFFICIENT_PERMISSIONS'
            }), 403
        
        # Get user from database
        try:
            from app import db
            
            if db is None:
                return jsonify({
                    'error': 'Database connection unavailable',
                    'code': 'DB_ERROR'
                }), 500
            
            user = db.users.find_one({'_id': payload['user_id']})
            
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'code': 'USER_NOT_FOUND'
                }), 401
            
            # Verify role in database matches token
            if user.get('role') != 'admin':
                return jsonify({
                    'error': 'Admin access required',
                    'code': 'INSUFFICIENT_PERMISSIONS'
                }), 403
            
            # Pass user to route function
            return f(user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_ERROR',
                'details': str(e)
            }), 500
    
    return decorated


def optional_auth(f: Callable) -> Callable:
    """
    Decorator for routes that work with or without authentication
    If token is provided and valid, user is passed to route
    If no token or invalid token, user is None
    
    Usage:
        @app.route('/public')
        @optional_auth
        def public_route(current_user):
            if current_user:
                return jsonify({'message': f'Hello {current_user["email"]}'})
            return jsonify({'message': 'Hello guest'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token_from_header()
        user = None
        
        if token:
            payload = verify_token(token)
            
            if payload:
                try:
                    from app import db
                    if db:
                        user = db.users.find_one({'_id': payload['user_id']})
                except Exception:
                    pass
        
        return f(user, *args, **kwargs)
    
    return decorated


def refresh_token(old_token: str) -> Optional[str]:
    """
    Refresh an existing token
    
    Args:
        old_token: Existing JWT token
        
    Returns:
        New token or None if refresh failed
    """
    payload = verify_token(old_token)
    
    if not payload:
        return None
    
    # Generate new token with same user info
    new_token = generate_token(
        user_id=payload['user_id'],
        email=payload['email'],
        role=payload.get('role', 'user')
    )
    
    return new_token


def revoke_token(token: str) -> bool:
    """
    Revoke a token (add to blacklist)
    Note: This requires a token blacklist implementation (Redis recommended)
    
    Args:
        token: Token to revoke
        
    Returns:
        True if revoked successfully
    """
    # TODO: Implement token blacklist using Redis
    # For now, return True as placeholder
    return True


def get_current_user_id() -> Optional[str]:
    """
    Get current user ID from request context
    
    Returns:
        User ID or None if not authenticated
    """
    token = extract_token_from_header()
    
    if not token:
        return None
    
    payload = verify_token(token)
    
    if not payload:
        return None
    
    return payload.get('user_id')


def get_current_user_role() -> Optional[str]:
    """
    Get current user role from request context
    
    Returns:
        User role or None if not authenticated
    """
    token = extract_token_from_header()
    
    if not token:
        return None
    
    payload = verify_token(token)
    
    if not payload:
        return None
    
    return payload.get('role')


def require_permissions(*permissions: str) -> Callable:
    """
    Decorator to require specific permissions
    
    Args:
        *permissions: Required permission names
        
    Usage:
        @app.route('/deploy')
        @require_permissions('deploy:create', 'deploy:execute')
        def deploy_route(current_user):
            return jsonify({'message': 'Deployment initiated'})
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            token = extract_token_from_header()
            
            if not token:
                return jsonify({
                    'error': 'Authentication token is missing',
                    'code': 'TOKEN_MISSING'
                }), 401
            
            payload = verify_token(token)
            
            if not payload:
                return jsonify({
                    'error': 'Invalid or expired token',
                    'code': 'TOKEN_INVALID'
                }), 401
            
            try:
                from app import db
                
                if db is None:
                    return jsonify({
                        'error': 'Database connection unavailable',
                        'code': 'DB_ERROR'
                    }), 500
                
                user = db.users.find_one({'_id': payload['user_id']})
                
                if not user:
                    return jsonify({
                        'error': 'User not found',
                        'code': 'USER_NOT_FOUND'
                    }), 401
                
                # Check permissions
                user_permissions = user.get('permissions', [])
                
                for permission in permissions:
                    if permission not in user_permissions and user.get('role') != 'admin':
                        return jsonify({
                            'error': f'Missing required permission: {permission}',
                            'code': 'INSUFFICIENT_PERMISSIONS'
                        }), 403
                
                return f(user, *args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'error': 'Permission check failed',
                    'code': 'PERMISSION_ERROR',
                    'details': str(e)
                }), 500
        
        return decorated
    
    return decorator
