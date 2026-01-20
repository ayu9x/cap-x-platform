from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import jwt
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def get_models():
    """Get models from app context"""
    from app import user_model, audit_model
    return user_model, audit_model

def token_required(f):
    """JWT token validation decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_model, _ = get_models()
            current_user = user_model.collection.find_one({'_id': data['user_id']})
            
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        user_model, audit_model = get_models()
        data = request.json
        
        # Validate required fields
        required = ['username', 'email', 'password', 'full_name']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if user_model.find_by_email(data['email']):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = user_model.create_user(data)
        
        # Log registration
        audit_model.log_action({
            'user_id': str(user['_id']),
            'username': user['username'],
            'action': 'register',
            'resource_type': 'user',
            'resource_id': str(user['_id']),
            'resource_name': user['username'],
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
        
        # Generate token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        user_model, audit_model = get_models()
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = user_model.find_by_email(data['email'])
        
        if not user or not user_model.verify_password(user, data['password']):
            # Log failed login
            if user:
                audit_model.log_action({
                    'user_id': str(user['_id']),
                    'username': user['username'],
                    'action': 'failed_login',
                    'resource_type': 'user',
                    'status': 'failed',
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent')
                })
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        user_model.update_last_login(user['_id'])
        
        # Log successful login
        audit_model.log_action({
            'user_id': str(user['_id']),
            'username': user['username'],
            'action': 'login',
            'resource_type': 'user',
            'resource_id': str(user['_id']),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
        
        # Generate token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['_id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'permissions': user['permissions']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user profile"""
    try:
        return jsonify({
            'user': {
                'id': str(current_user['_id']),
                'username': current_user['username'],
                'email': current_user['email'],
                'role': current_user['role'],
                'full_name': current_user['full_name'],
                'team': current_user.get('team'),
                'permissions': current_user['permissions'],
                'last_login': current_user.get('last_login')
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """User logout"""
    try:
        _, audit_model = get_models()
        
        # Log logout
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'logout',
            'resource_type': 'user',
            'resource_id': str(current_user['_id']),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
        
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500