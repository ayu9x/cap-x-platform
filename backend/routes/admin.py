from flask import Blueprint, request, jsonify
from routes.auth import token_required
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def get_models():
    from app import user_model, audit_model, db
    return user_model, audit_model, db

@admin_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users"""
    try:
        if current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        user_model, _, _ = get_models()
        users = user_model.get_all_users()
        
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """Update user"""
    try:
        if current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        user_model, audit_model, _ = get_models()
        data = request.json
        
        allowed_fields = ['role', 'status', 'team']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if update_data:
            user_model.update_user(user_id, update_data)
            
            audit_model.log_action({
                'user_id': str(current_user['_id']),
                'username': current_user['username'],
                'action': 'update_user',
                'resource_type': 'user',
                'resource_id': user_id,
                'changes': update_data,
                'ip_address': request.remote_addr
            })
        
        return jsonify({'message': 'User updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/audit-logs', methods=['GET'])
@token_required
def get_audit_logs(current_user):
    """Get audit logs"""
    try:
        if current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        _, audit_model, _ = get_models()
        
        limit = int(request.args.get('limit', 100))
        logs = audit_model.get_recent_logs(limit)
        
        return jsonify({'logs': logs}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/audit-logs/search', methods=['POST'])
@token_required
def search_audit_logs(current_user):
    """Search audit logs"""
    try:
        if current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        _, audit_model, _ = get_models()
        filters = request.json
        
        logs = audit_model.search_logs(filters)
        
        return jsonify({'logs': logs}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@token_required
def get_admin_stats(current_user):
    """Get admin statistics"""
    try:
        if current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        user_model, audit_model, db = get_models()
        
        stats = {
            'total_users': db.users.count_documents({}),
            'active_users': db.users.count_documents({'status': 'active'}),
            'total_applications': db.applications.count_documents({}),
            'total_deployments': db.deployments.count_documents({}),
            'total_incidents': db.incidents.count_documents({}),
            'open_incidents': db.incidents.count_documents({'status': {'$in': ['open', 'investigating']}}),
            'audit_stats': audit_model.get_audit_stats(days=30)
        }
        
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Get comprehensive dashboard statistics"""
    try:
        _, _, db = get_models()
        from models.deployment import Deployment
        from models.incident import Incident
        
        deployment_model = Deployment(db)
        incident_model = Incident(db)
        
        total_apps = db.applications.count_documents({})
        total_deployments = db.deployments.count_documents({})
        open_incidents = db.incidents.count_documents({'status': {'$in': ['open', 'investigating']}})
        
        deployment_stats = deployment_model.get_deployment_stats(days=7)
        incident_stats = incident_model.get_incident_stats(days=7)
        
        return jsonify({
            'overview': {
                'total_applications': total_apps,
                'total_deployments': total_deployments,
                'open_incidents': open_incidents,
                'active_users': db.users.count_documents({'status': 'active'})
            },
            'deployments': deployment_stats,
            'incidents': incident_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500