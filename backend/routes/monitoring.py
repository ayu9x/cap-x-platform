from flask import Blueprint, request, jsonify
from routes.auth import token_required

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

def get_models():
    from app import metric_model
    return metric_model

@monitoring_bp.route('/metrics', methods=['POST'])
@token_required
def record_metric(current_user):
    """Record a new metric"""
    try:
        metric_model = get_models()
        data = request.json
        
        metric = metric_model.record_metric(data)
        
        return jsonify({
            'message': 'Metric recorded',
            'metric': metric
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/metrics/batch', methods=['POST'])
@token_required
def record_metrics_batch(current_user):
    """Record multiple metrics"""
    try:
        metric_model = get_models()
        data = request.json
        
        if not isinstance(data.get('metrics'), list):
            return jsonify({'error': 'metrics must be an array'}), 400
        
        count = metric_model.record_metrics_batch(data['metrics'])
        
        return jsonify({
            'message': f'Recorded {count} metrics',
            'count': count
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/metrics/<application_id>', methods=['GET'])
@token_required
def get_metrics(current_user, application_id):
    """Get metrics for application"""
    try:
        metric_model = get_models()
        
        metric_type = request.args.get('type', 'cpu')
        hours = int(request.args.get('hours', 24))
        
        metrics = metric_model.get_metrics(application_id, metric_type, hours)
        
        return jsonify({'metrics': metrics}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/metrics/<application_id>/latest', methods=['GET'])
@token_required
def get_latest_metrics(current_user, application_id):
    """Get latest metrics for all types"""
    try:
        metric_model = get_models()
        
        metrics = metric_model.get_latest_metrics(application_id)
        
        return jsonify({'metrics': metrics}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/metrics/<application_id>/aggregates', methods=['GET'])
@token_required
def get_metric_aggregates(current_user, application_id):
    """Get aggregated metrics"""
    try:
        metric_model = get_models()
        
        metric_type = request.args.get('type', 'cpu')
        hours = int(request.args.get('hours', 24))
        
        aggregates = metric_model.get_metric_aggregates(application_id, metric_type, hours)
        
        return jsonify({'aggregates': aggregates}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/system', methods=['GET'])
@token_required
def get_system_metrics(current_user):
    """Get overall system metrics"""
    try:
        metric_model = get_models()
        
        metrics = metric_model.get_system_metrics()
        
        return jsonify({'system_metrics': metrics}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500