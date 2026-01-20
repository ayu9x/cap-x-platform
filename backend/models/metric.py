"""
Metric Model for CAP-X Platform
Stores application performance metrics
"""

from datetime import datetime, timedelta
from bson import ObjectId


class Metric:
    """Metric model for application performance tracking"""
    
    METRIC_TYPES = ['cpu', 'memory', 'latency', 'requests', 'errors', 'custom']
    
    @staticmethod
    def create(db, application_id, application_name, metric_type, value, **kwargs):
        """Create a new metric entry"""
        metric_data = {
            'application_id': ObjectId(application_id) if isinstance(application_id, str) else application_id,
            'application_name': application_name,
            'metric_type': metric_type,
            'value': value,
            'unit': kwargs.get('unit', ''),
            'timestamp': kwargs.get('timestamp', datetime.utcnow()),
            'environment': kwargs.get('environment', 'production'),
            'tags': kwargs.get('tags', {}),
            'metadata': kwargs.get('metadata', {})
        }
        
        result = db.metrics.insert_one(metric_data)
        metric_data['_id'] = result.inserted_id
        return metric_data
    
    @staticmethod
    def bulk_create(db, metrics_list):
        """Create multiple metrics at once"""
        if not metrics_list:
            return []
        
        result = db.metrics.insert_many(metrics_list)
        return result.inserted_ids
    
    @staticmethod
    def get_by_application(db, application_id, metric_type=None, start_time=None, end_time=None, limit=1000):
        """Get metrics for a specific application"""
        if isinstance(application_id, str):
            application_id = ObjectId(application_id)
        
        query = {'application_id': application_id}
        
        if metric_type:
            query['metric_type'] = metric_type
        
        if start_time or end_time:
            query['timestamp'] = {}
            if start_time:
                query['timestamp']['$gte'] = start_time
            if end_time:
                query['timestamp']['$lte'] = end_time
        
        metrics = list(
            db.metrics.find(query)
            .sort('timestamp', -1)
            .limit(limit)
        )
        
        return metrics
    
    @staticmethod
    def get_latest(db, application_id, metric_type):
        """Get the latest metric value for an application"""
        if isinstance(application_id, str):
            application_id = ObjectId(application_id)
        
        metric = db.metrics.find_one(
            {'application_id': application_id, 'metric_type': metric_type},
            sort=[('timestamp', -1)]
        )
        return metric
    
    @staticmethod
    def get_average(db, application_id, metric_type, start_time=None, end_time=None):
        """Get average metric value over a time period"""
        if isinstance(application_id, str):
            application_id = ObjectId(application_id)
        
        match_query = {
            'application_id': application_id,
            'metric_type': metric_type
        }
        
        if start_time or end_time:
            match_query['timestamp'] = {}
            if start_time:
                match_query['timestamp']['$gte'] = start_time
            if end_time:
                match_query['timestamp']['$lte'] = end_time
        
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': None,
                'avg_value': {'$avg': '$value'},
                'min_value': {'$min': '$value'},
                'max_value': {'$max': '$value'},
                'count': {'$sum': 1}
            }}
        ]
        
        result = list(db.metrics.aggregate(pipeline))
        return result[0] if result else None
    
    @staticmethod
    def get_time_series(db, application_id, metric_type, interval_minutes=5, hours=24):
        """Get time series data aggregated by interval"""
        if isinstance(application_id, str):
            application_id = ObjectId(application_id)
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {
                '$match': {
                    'application_id': application_id,
                    'metric_type': metric_type,
                    'timestamp': {'$gte': start_time}
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%dT%H:%M:00Z',
                            'date': {
                                '$subtract': [
                                    '$timestamp',
                                    {'$mod': [
                                        {'$toLong': '$timestamp'},
                                        interval_minutes * 60 * 1000
                                    ]}
                                ]
                            }
                        }
                    },
                    'avg_value': {'$avg': '$value'},
                    'min_value': {'$min': '$value'},
                    'max_value': {'$max': '$value'},
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}}
        ]
        
        return list(db.metrics.aggregate(pipeline))
    
    @staticmethod
    def cleanup_old_metrics(db, days=30):
        """Delete metrics older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = db.metrics.delete_many({'timestamp': {'$lt': cutoff_date}})
        return result.deleted_count
    
    @staticmethod
    def get_stats(db, application_id=None):
        """Get metric statistics"""
        query = {}
        if application_id:
            if isinstance(application_id, str):
                application_id = ObjectId(application_id)
            query['application_id'] = application_id
        
        total = db.metrics.count_documents(query)
        
        # Get metric type distribution
        pipeline = [
            {'$match': query},
            {'$group': {'_id': '$metric_type', 'count': {'$sum': 1}}}
        ]
        type_dist = list(db.metrics.aggregate(pipeline))
        
        return {
            'total_metrics': total,
            'metric_type_distribution': type_dist
        }