from flask import Blueprint, request, jsonify
from routes.auth import token_required

apps_bp = Blueprint('apps', __name__, url_prefix='/api/applications')

def get_models():
    """Get models from app context"""
    from app import app_model, audit_model
    return app_model, audit_model

@apps_bp.route('', methods=['GET'])
@token_required
def get_applications(current_user):
    """Get all applications"""
    try:
        app_model, _ = get_models()
        
        # Get filters from query params
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('team'):
            filters['team'] = request.args.get('team')
        
        apps = app_model.get_all_applications(filters)
        return jsonify({'applications': apps}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apps_bp.route('', methods=['POST'])
@token_required
def create_application(current_user):
    """Create new application"""
    try:
        app_model, audit_model = get_models()
        
        if 'create_app' not in current_user.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.json
        
        # Validate required fields
        required = ['name', 'description', 'repository_url']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if app already exists
        if app_model.get_application_by_name(data['name']):
            return jsonify({'error': 'Application already exists'}), 400
        
        app = app_model.create_application(data, str(current_user['_id']))
        
        # Log action
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'create',
            'resource_type': 'application',
            'resource_id': str(app['_id']),
            'resource_name': app['name'],
            'details': {'description': app['description']},
            'ip_address': request.remote_addr
        })
        
        return jsonify({
            'message': 'Application created successfully',
            'application': app
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apps_bp.route('/<app_id>', methods=['GET'])
@token_required
def get_application(current_user, app_id):
    """Get application by ID"""
    try:
        app_model, _ = get_models()
        app = app_model.get_application_by_id(app_id)
        
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        return jsonify({'application': app}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apps_bp.route('/<app_id>', methods=['PUT'])
@token_required
def update_application(current_user, app_id):
    """Update application"""
    try:
        app_model, audit_model = get_models()
        
        if 'create_app' not in current_user.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        app = app_model.get_application_by_id(app_id)
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        data = request.json
        update_fields = {}
        
        allowed_fields = ['description', 'repository_url', 'status', 'team']
        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]
        
        if update_fields:
            app_model.update_application(app_id, update_fields)
            
            # Log action
            audit_model.log_action({
                'user_id': str(current_user['_id']),
                'username': current_user['username'],
                'action': 'update',
                'resource_type': 'application',
                'resource_id': app_id,
                'resource_name': app['name'],
                'changes': update_fields,
                'ip_address': request.remote_addr
            })
        
        return jsonify({'message': 'Application updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apps_bp.route('/<app_id>', methods=['DELETE'])
@token_required
def delete_application(current_user, app_id):
    """Delete application"""
    try:
        app_model, audit_model = get_models()
        
        if 'delete_app' not in current_user.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        app = app_model.get_application_by_id(app_id)
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        app_model.delete_application(app_id)
        
        # Log action
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'delete',
            'resource_type': 'application',
            'resource_id': app_id,
            'resource_name': app['name'],
            'ip_address': request.remote_addr
        })
        
        return jsonify({'message': 'Application deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@apps_bp.route('/<app_id>/health', methods=['PUT'])
@token_required
def update_application_health(current_user, app_id):
    """Update application health status"""
    try:
        app_model, _ = get_models()
        data = request.json
        
        if not data.get('health_status'):
            return jsonify({'error': 'health_status required'}), 400
        
        environment = data.get('environment', 'production')
        app_model.update_health_status(app_id, data['health_status'], environment)
        
        return jsonify({'message': 'Health status updated'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500