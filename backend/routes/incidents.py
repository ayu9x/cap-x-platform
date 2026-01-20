from flask import Blueprint, request, jsonify
from routes.auth import token_required

incidents_bp = Blueprint('incidents', __name__, url_prefix='/api/incidents')

def get_models():
    from app import incident_model, app_model, audit_model
    return incident_model, app_model, audit_model

@incidents_bp.route('', methods=['GET'])
@token_required
def get_incidents(current_user):
    """Get incidents"""
    try:
        incident_model, _, _ = get_models()
        
        app_id = request.args.get('application_id')
        status = request.args.get('status')
        
        if app_id:
            incidents = incident_model.get_incidents_by_application(app_id)
        elif status == 'open':
            incidents = incident_model.get_open_incidents()
        else:
            incidents = incident_model.get_open_incidents()
        
        return jsonify({'incidents': incidents}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('', methods=['POST'])
@token_required
def create_incident(current_user):
    """Create new incident"""
    try:
        incident_model, app_model, audit_model = get_models()
        
        data = request.json
        
        required = ['application_id', 'title', 'description', 'severity']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        incident = incident_model.create_incident(data)
        app_model.increment_incident_count(data['application_id'])
        
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'create_incident',
            'resource_type': 'incident',
            'resource_id': str(incident['_id']),
            'resource_name': data['title'],
            'details': {'severity': data['severity']},
            'ip_address': request.remote_addr
        })
        
        return jsonify({
            'message': 'Incident created',
            'incident': incident
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<incident_id>', methods=['GET'])
@token_required
def get_incident(current_user, incident_id):
    """Get incident by ID"""
    try:
        incident_model, _, _ = get_models()
        incident = incident_model.get_incident_by_id(incident_id)
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        return jsonify({'incident': incident}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<incident_id>/status', methods=['PUT'])
@token_required
def update_incident_status(current_user, incident_id):
    """Update incident status"""
    try:
        incident_model, _, audit_model = get_models()
        data = request.json
        
        if not data.get('status'):
            return jsonify({'error': 'status required'}), 400
        
        incident_model.update_incident_status(
            incident_id,
            data['status'],
            current_user['username'],
            data.get('details')
        )
        
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'update_incident_status',
            'resource_type': 'incident',
            'resource_id': incident_id,
            'details': {'new_status': data['status']},
            'ip_address': request.remote_addr
        })
        
        return jsonify({'message': 'Incident status updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<incident_id>/healing', methods=['POST'])
@token_required
def record_auto_healing(current_user, incident_id):
    """Record auto-healing attempt"""
    try:
        incident_model, _, _ = get_models()
        data = request.json
        
        incident_model.add_auto_healing_action(
            incident_id,
            data.get('action'),
            data.get('success', False)
        )
        
        return jsonify({'message': 'Auto-healing action recorded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/stats', methods=['GET'])
@token_required
def get_incident_stats(current_user):
    """Get incident statistics"""
    try:
        incident_model, _, _ = get_models()
        
        days = int(request.args.get('days', 30))
        stats = incident_model.get_incident_stats(days)
        
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500