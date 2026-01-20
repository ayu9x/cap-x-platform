"""
Audit Log Model for CAP-X Platform
Tracks all user actions for security and compliance
"""

from datetime import datetime, timedelta
from bson import ObjectId


class AuditLog:
    """Audit log model for security tracking"""
    
    ACTIONS = [
        'user_login', 'user_logout', 'user_created', 'user_updated', 'user_deleted',
        'app_created', 'app_updated', 'app_deleted',
        'deployment_created', 'deployment_failed', 'deployment_success', 'deployment_rollback',
        'pipeline_triggered', 'pipeline_cancelled',
        'incident_created', 'incident_resolved',
        'config_changed', 'permission_changed', 'other'
    ]
    
    @staticmethod
    def create(db, user_id, username, action, resource_type, resource_id=None, **kwargs):
        """Create a new audit log entry"""
        log_data = {
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'username': username,
            'action': action,
            'resource_type': resource_type,
            'resource_id': ObjectId(resource_id) if isinstance(resource_id, str) and resource_id else resource_id,
            'timestamp': datetime.utcnow(),
            'ip_address': kwargs.get('ip_address', 'unknown'),
            'user_agent': kwargs.get('user_agent', 'unknown'),
            'status': kwargs.get('status', 'success'),
            'details': kwargs.get('details', {}),
            'changes': kwargs.get('changes', {}),
            'error_message': kwargs.get('error_message', None)
        }
        
        result = db.audit_logs.insert_one(log_data)
        log_data['_id'] = result.inserted_id
        return log_data
    
    @staticmethod
    def get_by_user(db, user_id, skip=0, limit=50):
        """Get audit logs for a specific user"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        logs = list(
            db.audit_logs.find({'user_id': user_id})
            .skip(skip)
            .limit(limit)
            .sort('timestamp', -1)
        )
        total = db.audit_logs.count_documents({'user_id': user_id})
        
        return {
            'logs': logs,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def get_by_resource(db, resource_type, resource_id, skip=0, limit=50):
        """Get audit logs for a specific resource"""
        if isinstance(resource_id, str):
            resource_id = ObjectId(resource_id)
        
        logs = list(
            db.audit_logs.find({
                'resource_type': resource_type,
                'resource_id': resource_id
            })
            .skip(skip)
            .limit(limit)
            .sort('timestamp', -1)
        )
        total = db.audit_logs.count_documents({
            'resource_type': resource_type,
            'resource_id': resource_id
        })
        
        return {
            'logs': logs,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def list_all(db, skip=0, limit=100, action=None, start_time=None, end_time=None):
        """List all audit logs with filters"""
        query = {}
        
        if action:
            query['action'] = action
        
        if start_time or end_time:
            query['timestamp'] = {}
            if start_time:
                query['timestamp']['$gte'] = start_time
            if end_time:
                query['timestamp']['$lte'] = end_time
        
        logs = list(
            db.audit_logs.find(query)
            .skip(skip)
            .limit(limit)
            .sort('timestamp', -1)
        )
        total = db.audit_logs.count_documents(query)
        
        return {
            'logs': logs,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def get_recent(db, limit=50):
        """Get recent audit logs"""
        return list(
            db.audit_logs.find()
            .sort('timestamp', -1)
            .limit(limit)
        )
    
    @staticmethod
    def search(db, search_term, skip=0, limit=50):
        """Search audit logs"""
        query = {
            '$or': [
                {'username': {'$regex': search_term, '$options': 'i'}},
                {'action': {'$regex': search_term, '$options': 'i'}},
                {'resource_type': {'$regex': search_term, '$options': 'i'}}
            ]
        }
        
        logs = list(
            db.audit_logs.find(query)
            .skip(skip)
            .limit(limit)
            .sort('timestamp', -1)
        )
        total = db.audit_logs.count_documents(query)
        
        return {
            'logs': logs,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def cleanup_old_logs(db, days=90):
        """Delete audit logs older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = db.audit_logs.delete_many({'timestamp': {'$lt': cutoff_date}})
        return result.deleted_count
    
    @staticmethod
    def get_stats(db, start_time=None, end_time=None):
        """Get audit log statistics"""
        query = {}
        if start_time or end_time:
            query['timestamp'] = {}
            if start_time:
                query['timestamp']['$gte'] = start_time
            if end_time:
                query['timestamp']['$lte'] = end_time
        
        total = db.audit_logs.count_documents(query)
        
        # Get action distribution
        pipeline = [
            {'$match': query},
            {'$group': {'_id': '$action', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        action_dist = list(db.audit_logs.aggregate(pipeline))
        
        # Get user activity
        user_pipeline = [
            {'$match': query},
            {'$group': {'_id': '$username', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        top_users = list(db.audit_logs.aggregate(user_pipeline))
        
        return {
            'total_logs': total,
            'action_distribution': action_dist,
            'top_users': top_users
        }