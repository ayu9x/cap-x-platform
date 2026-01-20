from flask import Blueprint, request, jsonify
from routes.auth import token_required

pipelines_bp = Blueprint('pipelines', __name__, url_prefix='/api/pipelines')

def get_models():
    from app import pipeline_model, audit_model
    return pipeline_model, audit_model

@pipelines_bp.route('', methods=['GET'])
@token_required
def get_pipelines(current_user):
    """Get recent pipelines"""
    try:
        pipeline_model, _ = get_models()
        limit = int(request.args.get('limit', 10))
        app_id = request.args.get('application_id')
        
        if app_id:
            pipelines = pipeline_model.get_pipelines_by_application(app_id, limit)
        else:
            pipelines = pipeline_model.get_recent_pipelines(limit)
        
        return jsonify({'pipelines': pipelines}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pipelines_bp.route('', methods=['POST'])
@token_required
def create_pipeline(current_user):
    """Create new pipeline execution"""
    try:
        pipeline_model, audit_model = get_models()
        
        if 'trigger_pipeline' not in current_user.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.json
        data['triggered_by'] = current_user['username']
        
        pipeline = pipeline_model.create_pipeline(data)
        
        audit_model.log_action({
            'user_id': str(current_user['_id']),
            'username': current_user['username'],
            'action': 'trigger_pipeline',
            'resource_type': 'pipeline',
            'resource_id': str(pipeline['_id']),
            'resource_name': data.get('pipeline_name'),
            'ip_address': request.remote_addr
        })
        
        return jsonify({
            'message': 'Pipeline created',
            'pipeline': pipeline
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pipelines_bp.route('/<pipeline_id>', methods=['GET'])
@token_required
def get_pipeline(current_user, pipeline_id):
    """Get pipeline by ID"""
    try:
        pipeline_model, _ = get_models()
        pipeline = pipeline_model.get_pipeline_by_id(pipeline_id)
        
        if not pipeline:
            return jsonify({'error': 'Pipeline not found'}), 404
        
        return jsonify({'pipeline': pipeline}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pipelines_bp.route('/<pipeline_id>/status', methods=['PUT'])
@token_required
def update_pipeline_status(current_user, pipeline_id):
    """Update pipeline status"""
    try:
        pipeline_model, _ = get_models()
        data = request.json
        
        pipeline_model.update_pipeline_status(
            pipeline_id,
            data.get('status'),
            data.get('error_message')
        )
        
        return jsonify({'message': 'Pipeline status updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pipelines_bp.route('/<pipeline_id>/stages/<stage_name>', methods=['PUT'])
@token_required
def update_stage_status(current_user, pipeline_id, stage_name):
    """Update stage status"""
    try:
        pipeline_model, _ = get_models()
        data = request.json
        
        pipeline_model.update_stage_status(
            pipeline_id,
            stage_name,
            data.get('status'),
            data.get('data')
        )
        
        return jsonify({'message': 'Stage status updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pipelines_bp.route('/stats', methods=['GET'])
@token_required
def get_pipeline_stats(current_user):
    """Get pipeline statistics"""
    try:
        pipeline_model, _ = get_models()
        
        app_id = request.args.get('application_id')
        days = int(request.args.get('days', 30))
        
        stats = pipeline_model.get_pipeline_stats(app_id, days)
        
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500