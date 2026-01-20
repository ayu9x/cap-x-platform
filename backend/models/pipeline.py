"""
Pipeline Model for CAP-X Platform
Tracks CI/CD pipeline executions
"""

from datetime import datetime
from bson import ObjectId


class Pipeline:
    """Pipeline model for CI/CD tracking"""
    
    STATUSES = ['queued', 'running', 'success', 'failed', 'cancelled']
    TRIGGERS = ['manual', 'push', 'pull_request', 'schedule', 'api']
    
    @staticmethod
    def create(db, application_id, application_name, trigger, triggered_by, **kwargs):
        """Create a new pipeline run"""
        pipeline_data = {
            'application_id': ObjectId(application_id) if isinstance(application_id, str) else application_id,
            'application_name': application_name,
            'status': 'queued',
            'trigger': trigger,
            'triggered_by': triggered_by,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'started_at': None,
            'completed_at': None,
            'duration_seconds': 0,
            'branch': kwargs.get('branch', 'main'),
            'commit_hash': kwargs.get('commit_hash', ''),
            'commit_message': kwargs.get('commit_message', ''),
            'stages': [
                {'name': 'build', 'status': 'pending', 'started_at': None, 'completed_at': None, 'logs': []},
                {'name': 'test', 'status': 'pending', 'started_at': None, 'completed_at': None, 'logs': []},
                {'name': 'deploy', 'status': 'pending', 'started_at': None, 'completed_at': None, 'logs': []}
            ],
            'environment': kwargs.get('environment', 'development'),
            'artifacts': [],
            'error_message': None,
            'metadata': kwargs.get('metadata', {})
        }
        
        result = db.pipelines.insert_one(pipeline_data)
        pipeline_data['_id'] = result.inserted_id
        return pipeline_data
    
    @staticmethod
    def get_by_id(db, pipeline_id):
        """Get pipeline by ID"""
        if isinstance(pipeline_id, str):
            pipeline_id = ObjectId(pipeline_id)
        return db.pipelines.find_one({'_id': pipeline_id})
    
    @staticmethod
    def update_status(db, pipeline_id, status, error_message=None):
        """Update pipeline status"""
        if isinstance(pipeline_id, str):
            pipeline_id = ObjectId(pipeline_id)
        
        if status not in Pipeline.STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {Pipeline.STATUSES}")
        
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if status == 'running' and not db.pipelines.find_one({'_id': pipeline_id}).get('started_at'):
            update_data['started_at'] = datetime.utcnow()
        
        if status in ['success', 'failed', 'cancelled']:
            update_data['completed_at'] = datetime.utcnow()
            
            # Calculate duration
            pipeline = db.pipelines.find_one({'_id': pipeline_id})
            if pipeline and pipeline.get('started_at'):
                duration = (update_data['completed_at'] - pipeline['started_at']).total_seconds()
                update_data['duration_seconds'] = round(duration, 2)
        
        if error_message:
            update_data['error_message'] = error_message
        
        result = db.pipelines.update_one(
            {'_id': pipeline_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_stage(db, pipeline_id, stage_name, status, logs=None):
        """Update a specific pipeline stage"""
        if isinstance(pipeline_id, str):
            pipeline_id = ObjectId(pipeline_id)
        
        pipeline = db.pipelines.find_one({'_id': pipeline_id})
        if not pipeline:
            return False
        
        # Find the stage index
        stage_index = None
        for i, stage in enumerate(pipeline['stages']):
            if stage['name'] == stage_name:
                stage_index = i
                break
        
        if stage_index is None:
            return False
        
        update_data = {
            f'stages.{stage_index}.status': status,
            'updated_at': datetime.utcnow()
        }
        
        if status == 'running' and not pipeline['stages'][stage_index].get('started_at'):
            update_data[f'stages.{stage_index}.started_at'] = datetime.utcnow()
        
        if status in ['success', 'failed', 'skipped']:
            update_data[f'stages.{stage_index}.completed_at'] = datetime.utcnow()
        
        if logs:
            for log in logs:
                db.pipelines.update_one(
                    {'_id': pipeline_id},
                    {'$push': {f'stages.{stage_index}.logs': log}}
                )
        
        result = db.pipelines.update_one(
            {'_id': pipeline_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_artifact(db, pipeline_id, artifact_name, artifact_url):
        """Add an artifact to pipeline"""
        if isinstance(pipeline_id, str):
            pipeline_id = ObjectId(pipeline_id)
        
        artifact = {
            'name': artifact_name,
            'url': artifact_url,
            'created_at': datetime.utcnow()
        }
        
        result = db.pipelines.update_one(
            {'_id': pipeline_id},
            {
                '$push': {'artifacts': artifact},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def list_by_application(db, application_id, skip=0, limit=20):
        """List pipelines for a specific application"""
        if isinstance(application_id, str):
            application_id = ObjectId(application_id)
        
        pipelines = list(
            db.pipelines.find({'application_id': application_id})
            .skip(skip)
            .limit(limit)
            .sort('created_at', -1)
        )
        total = db.pipelines.count_documents({'application_id': application_id})
        
        return {
            'pipelines': pipelines,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def list_all(db, skip=0, limit=50, status=None):
        """List all pipelines with pagination and filters"""
        query = {}
        if status:
            query['status'] = status
        
        pipelines = list(
            db.pipelines.find(query)
            .skip(skip)
            .limit(limit)
            .sort('created_at', -1)
        )
        total = db.pipelines.count_documents(query)
        
        return {
            'pipelines': pipelines,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def get_recent(db, limit=10):
        """Get recent pipeline runs"""
        return list(
            db.pipelines.find()
            .sort('created_at', -1)
            .limit(limit)
        )
    
    @staticmethod
    def get_stats(db, application_id=None):
        """Get pipeline statistics"""
        query = {}
        if application_id:
            if isinstance(application_id, str):
                application_id = ObjectId(application_id)
            query['application_id'] = application_id
        
        total = db.pipelines.count_documents(query)
        success = db.pipelines.count_documents({**query, 'status': 'success'})
        failed = db.pipelines.count_documents({**query, 'status': 'failed'})
        running = db.pipelines.count_documents({**query, 'status': 'running'})
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        # Get average duration
        pipeline_avg = [
            {'$match': {**query, 'status': 'success', 'duration_seconds': {'$gt': 0}}},
            {'$group': {
                '_id': None,
                'avg_duration': {'$avg': '$duration_seconds'}
            }}
        ]
        avg_result = list(db.pipelines.aggregate(pipeline_avg))
        avg_duration = avg_result[0]['avg_duration'] if avg_result else 0
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'running': running,
            'success_rate': round(success_rate, 2),
            'avg_duration_seconds': round(avg_duration, 2)
        }