"""
User Model for CAP-X Platform
Handles user authentication, authorization, and RBAC
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId


class User:
    """User model with authentication and RBAC"""
    
    ROLES = ['admin', 'developer', 'viewer']
    
    PERMISSIONS = {
        'admin': [
            'create_user', 'delete_user', 'update_user', 'view_users',
            'create_app', 'delete_app', 'update_app', 'view_apps',
            'deploy', 'rollback', 'view_deployments',
            'trigger_pipeline', 'view_pipelines',
            'resolve_incident', 'view_incidents',
            'view_metrics', 'configure_monitoring',
            'manage_infrastructure'
        ],
        'developer': [
            'create_app', 'update_app', 'view_apps',
            'deploy', 'rollback', 'view_deployments',
            'trigger_pipeline', 'view_pipelines',
            'view_incidents', 'view_metrics'
        ],
        'viewer': [
            'view_apps', 'view_deployments', 'view_pipelines',
            'view_incidents', 'view_metrics'
        ]
    }
    
    @staticmethod
    def create(db, username, email, password, full_name, role='developer'):
        """Create a new user"""
        if role not in User.ROLES:
            raise ValueError(f"Invalid role. Must be one of: {User.ROLES}")
        
        # Check if user already exists
        if db.users.find_one({'email': email}):
            raise ValueError("User with this email already exists")
        
        if db.users.find_one({'username': username}):
            raise ValueError("User with this username already exists")
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'full_name': full_name,
            'role': role,
            'permissions': User.PERMISSIONS.get(role, []),
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None,
            'metadata': {
                'login_count': 0,
                'failed_login_attempts': 0
            }
        }
        
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return user_data
    
    @staticmethod
    def authenticate(db, email, password):
        """Authenticate user with email and password"""
        user = db.users.find_one({'email': email})
        
        if not user:
            return None
        
        if not user.get('is_active', True):
            return None
        
        if check_password_hash(user['password_hash'], password):
            # Update last login and login count
            db.users.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'last_login': datetime.utcnow(),
                        'metadata.failed_login_attempts': 0
                    },
                    '$inc': {'metadata.login_count': 1}
                }
            )
            return user
        else:
            # Increment failed login attempts
            db.users.update_one(
                {'_id': user['_id']},
                {'$inc': {'metadata.failed_login_attempts': 1}}
            )
            return None
    
    @staticmethod
    def get_by_id(db, user_id):
        """Get user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return db.users.find_one({'_id': user_id})
    
    @staticmethod
    def get_by_email(db, email):
        """Get user by email"""
        return db.users.find_one({'email': email})
    
    @staticmethod
    def update(db, user_id, update_data):
        """Update user information"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        update_data['updated_at'] = datetime.utcnow()
        
        # If role is being updated, update permissions too
        if 'role' in update_data:
            update_data['permissions'] = User.PERMISSIONS.get(update_data['role'], [])
        
        result = db.users.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(db, user_id):
        """Delete user (soft delete by setting is_active to False)"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = db.users.update_one(
            {'_id': user_id},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def list_all(db, skip=0, limit=50, role=None):
        """List all users with pagination"""
        query = {}
        if role:
            query['role'] = role
        
        users = list(db.users.find(query).skip(skip).limit(limit).sort('created_at', -1))
        total = db.users.count_documents(query)
        
        return {
            'users': users,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def has_permission(user, permission):
        """Check if user has a specific permission"""
        return permission in user.get('permissions', [])
    
    @staticmethod
    def change_password(db, user_id, old_password, new_password):
        """Change user password"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        user = db.users.find_one({'_id': user_id})
        if not user:
            return False
        
        if not check_password_hash(user['password_hash'], old_password):
            return False
        
        result = db.users.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'password_hash': generate_password_hash(new_password),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0