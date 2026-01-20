from flask import Blueprint, request, jsonify
from routes.auth import token_required

deployments_bp = Blueprint('deployments', __name__, url_prefix='/api/deployments')

def get_models():
    """Get models from app context"""
    from app import deployment_model, app_model, audit_model
    return deployment_model, app_model, audit_model

@deployments_bp.route('', methods=['GET'])
@token_required
def get_deployments(current_user):
    """Get recent deployments"""
    try:
        deployment_model, _, _ = get_models()
        limit = int(request.args.get('limit', 20))
        
        # Get by application if specified
        app_id = request.args.get('application_id')
        if app_id:
            deployments = deployment_model.get_deployments_by_application(app_id, limit)
        else:
            deployments = deployment_model.get_recent_deployments(limit=limit)
        
        return jsonify({'deployments': deployments}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('', methods=['POST'])
@token_required
def create_deployment(current_user):
    """Create new deployment"""
    try:
        deployment_model, app_model, audit_model = get_models()
        
        if 'deploy' not in current_user.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.json
        
        # Validate required fields
        required = ['application_id', 'application_name', 'version', 'environment']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Set deployed_by
        data['deployed_by'] = current_user['username']
        
        # Create deployment
        deployment = deployment_model.create_deployment(data)
        
        # Increment deployment counter
        app_model.increment_deployment_count(data['application_id'])
        
        # Log action
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'deploy',
            'resource_type': 'deployment',
            'resource_id': str(deployment['_id']),
            'resource_name': f"{data['application_name']}-{data['version']}",
            'details': {
                'environment': data['environment'],
                'version': data['version']
            },
            'ip_address': request.remote_addr
        })
        
        return jsonify({
            'message': 'Deployment initiated',
            'deployment': deployment
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('/<deployment_id>', methods=['GET'])
@token_required
def get_deployment(current_user, deployment_id):
    """Get deployment by ID"""
    try:
        deployment_model, _, _ = get_models()
        deployment = deployment_model.get_deployment_by_id(deployment_id)
        
        if not deployment:
            return jsonify({'error': 'Deployment not found'}), 404
        
        return jsonify({'deployment': deployment}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('/<deployment_id>/status', methods=['PUT'])
@token_required
def update_deployment_status(current_user, deployment_id):
    """Update deployment status"""
    try:
        deployment_model, _, audit_model = get_models()
        data = request.json
        
        if not data.get('status'):
            return jsonify({'error': 'status required'}), 400
        
        deployment = deployment_model.get_deployment_by_id(deployment_id)
        if not deployment:
            return jsonify({'error': 'Deployment not found'}), 404
        
        deployment_model.update_deployment_status(
            deployment_id,
            data.get('status'),
            data.get('error_message')
        )
        
        # Log action
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'update_deployment_status',
            'resource_type': 'deployment',
            'resource_id': deployment_id,
            'details': {'new_status': data.get('status')},
            'ip_address': request.remote_addr
        })
        
        return jsonify({'message': 'Status updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('/<deployment_id>/logs', methods=['POST'])
@token_required
def add_deployment_log(current_user, deployment_id):
    """Add log entry to deployment"""
    try:
        deployment_model, _, _ = get_models()
        data = request.json
        
        if not data.get('message'):
            return jsonify({'error': 'message required'}), 400
        
        deployment_model.add_deployment_log(deployment_id, data['message'])
        
        return jsonify({'message': 'Log added'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('/stats', methods=['GET'])
@token_required
def get_deployment_stats(current_user):
    """Get deployment statistics"""
    try:
        deployment_model, _, _ = get_models()
        
        app_id = request.args.get('application_id')
        days = int(request.args.get('days', 30))
        
        stats = deployment_model.get_deployment_stats(app_id, days)
        
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500