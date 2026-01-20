"""
Deployment Model for CAP-X Platform
Tracks deployment history and metrics
"""

from datetime import datetime
from bson import ObjectId


class Deployment:
    """Deployment model for tracking application deployments"""
    
    STATUSES = ['pending', 'in_progress', 'success', 'failed', 'rolled_back']
    STRATEGIES = ['rolling', 'blue_green', 'canary', 'recreate']
    ENVIRONMENTS = ['development', 'staging', 'production']
    
    @staticmethod
    def create(db, application_id, application_name, version, environment, deployed_by, **kwargs):
        """Create a new deployment record"""
        deployment_data = {
            'application_id': ObjectId(application_id) if isinstance(application_id, str) else application_id,
            'application_name': application_name,
            'version': version,
            'environment': environment,
            'status': 'pending',
            'deployed_by': deployed_by,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'started_at': None,
            'completed_at': None,
            'deployment_strategy': kwargs.get('strategy', 'rolling'),
            'commit_hash': kwargs.get('commit_hash', ''),
            'branch': kwargs.get('branch', 'main'),
            'docker_image': kwargs.get('docker_image', ''),
            'replicas': kwargs.get('replicas', 3),
            'metrics': {
                'deployment_duration': 0,
                'success_rate': 0,
                'rollback_count': 0,
                'health_check_passed': False
            },
            'logs': [],
            'error_message': None,
            'rollback_from': kwargs.get('rollback_from', None),
            'metadata': kwargs.get('metadata', {})
        }
        
        result = db.deployments.insert_one(deployment_data)
        deployment_data['_id'] = result.inserted_id
        return deployment_data
    
    @staticmethod
    def get_by_id(db, deployment_id):
        """Get deployment by ID"""
        if isinstance(deployment_id, str):
            deployment_id = ObjectId(deployment_id)
        return db.deployments.find_one({'_id': deployment_id})
    
    @staticmethod
    def update_status(db, deployment_id, status, error_message=None):
        """Update deployment status"""
        if isinstance(deployment_id, str):
            deployment_id = ObjectId(deployment_id)
        
        if status not in Deployment.STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {Deployment.STATUSES}")
        
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if status == 'in_progress' and not db.deployments.find_one({'_id': deployment_id}).get('started_at'):
            update_data['started_at'] = datetime.utcnow()
        
        if status in ['success', 'failed', 'rolled_back']:
            update_data['completed_at'] = datetime.utcnow()
            
            # Calculate deployment duration
            deployment = db.deployments.find_one({'_id': deployment_id})
            if deployment and deployment.get('started_at'):
                duration = (update_data['completed_at'] - deployment['started_at']).total_seconds()
                update_data['metrics.deployment_duration'] = duration
        
        if error_message:
            update_data['error_message'] = error_message
        
        result = db.deployments.update_one(
            {'_id': deployment_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_log(db, deployment_id, log_message, level='info'):
        """Add a log entry to deployment"""
        if isinstance(deployment_id, str):
            deployment_id = ObjectId(deployment_id)
        
        log_entry = {
            'timestamp': datetime.utcnow(),
            'level': level,
            'message': log_message
        }
        
        result = db.deployments.update_one(
            {'_id': deployment_id},
            {
                '$push': {'logs': log_entry},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def list_by_application(db, application_id, skip=0, limit=20):
        """List deployments for a specific application"""
        if isinstance(application_id, str):
            application_id = ObjectId(application_id)
        
        deployments = list(
            db.deployments.find({'application_id': application_id})
            .skip(skip)
            .limit(limit)
            .sort('created_at', -1)
        )
        total = db.deployments.count_documents({'application_id': application_id})
        
        return {
            'deployments': deployments,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def list_all(db, skip=0, limit=50, status=None, environment=None):
        """List all deployments with pagination and filters"""
        query = {}
        if status:
            query['status'] = status
        if environment:
            query['environment'] = environment
        
        deployments = list(
            db.deployments.find(query)
            .skip(skip)
            .limit(limit)
            .sort('created_at', -1)
        )
        total = db.deployments.count_documents(query)
        
        return {
            'deployments': deployments,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def get_recent(db, limit=10):
        """Get recent deployments"""
        return list(
            db.deployments.find()
            .sort('created_at', -1)
            .limit(limit)
        )
    
    @staticmethod
    def get_stats(db, application_id=None):
        """Get deployment statistics"""
        query = {}
        if application_id:
            if isinstance(application_id, str):
                application_id = ObjectId(application_id)
            query['application_id'] = application_id
        
        total = db.deployments.count_documents(query)
        success = db.deployments.count_documents({**query, 'status': 'success'})
        failed = db.deployments.count_documents({**query, 'status': 'failed'})
        in_progress = db.deployments.count_documents({**query, 'status': 'in_progress'})
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        # Get average deployment duration
        pipeline = [
            {'$match': {**query, 'status': 'success'}},
            {'$group': {
                '_id': None,
                'avg_duration': {'$avg': '$metrics.deployment_duration'}
            }}
        ]
        avg_result = list(db.deployments.aggregate(pipeline))
        avg_duration = avg_result[0]['avg_duration'] if avg_result else 0
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'in_progress': in_progress,
            'success_rate': round(success_rate, 2),
            'avg_deployment_duration': round(avg_duration, 2)
        }
    
    @staticmethod
    def create_rollback(db, original_deployment_id, deployed_by):
        """Create a rollback deployment"""
        if isinstance(original_deployment_id, str):
            original_deployment_id = ObjectId(original_deployment_id)
        
        original = db.deployments.find_one({'_id': original_deployment_id})
        if not original:
            raise ValueError("Original deployment not found")
        
        # Find the last successful deployment before this one
        last_success = db.deployments.find_one({
            'application_id': original['application_id'],
            'environment': original['environment'],
            'status': 'success',
            'created_at': {'$lt': original['created_at']}
        }, sort=[('created_at', -1)])
        
        if not last_success:
            raise ValueError("No previous successful deployment found to rollback to")
        
        # Create new deployment with previous version
        rollback_deployment = Deployment.create(
            db,
            application_id=original['application_id'],
            application_name=original['application_name'],
            version=last_success['version'],
            environment=original['environment'],
            deployed_by=deployed_by,
            commit_hash=last_success.get('commit_hash', ''),
            docker_image=last_success.get('docker_image', ''),
            rollback_from=original_deployment_id
        )
        
        # Update original deployment status
        Deployment.update_status(db, original_deployment_id, 'rolled_back')
        
        return rollback_deployment