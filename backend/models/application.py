"""
Application Model for CAP-X Platform
Manages application registry and metadata
"""

from datetime import datetime
from bson import ObjectId


class Application:
    """Application model for service registry"""
    
    STATUSES = ['active', 'inactive', 'archived', 'deploying']
    LANGUAGES = ['python', 'javascript', 'java', 'go', 'ruby', 'php', 'other']
    FRAMEWORKS = ['flask', 'django', 'express', 'react', 'vue', 'angular', 'spring', 'rails', 'other']
    
    @staticmethod
    def create(db, name, description, repository_url, language, framework, created_by, **kwargs):
        """Create a new application"""
        # Check if application already exists
        if db.applications.find_one({'name': name}):
            raise ValueError(f"Application '{name}' already exists")
        
        app_data = {
            'name': name,
            'description': description,
            'repository_url': repository_url,
            'language': language,
            'framework': framework,
            'status': 'active',
            'created_by': created_by,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'environments': {
                'development': {
                    'url': kwargs.get('dev_url', ''),
                    'version': '0.0.0',
                    'health_status': 'unknown',
                    'last_deployed': None
                },
                'staging': {
                    'url': kwargs.get('staging_url', ''),
                    'version': '0.0.0',
                    'health_status': 'unknown',
                    'last_deployed': None
                },
                'production': {
                    'url': kwargs.get('prod_url', ''),
                    'version': '0.0.0',
                    'health_status': 'unknown',
                    'last_deployed': None
                }
            },
            'metadata': {
                'total_deployments': 0,
                'successful_deployments': 0,
                'failed_deployments': 0,
                'uptime_percentage': 100.0,
                'avg_deployment_duration': 0,
                'last_incident': None,
                'total_incidents': 0
            },
            'tags': kwargs.get('tags', []),
            'team': kwargs.get('team', ''),
            'owner': kwargs.get('owner', created_by)
        }
        
        result = db.applications.insert_one(app_data)
        app_data['_id'] = result.inserted_id
        return app_data
    
    @staticmethod
    def get_by_id(db, app_id):
        """Get application by ID"""
        if isinstance(app_id, str):
            app_id = ObjectId(app_id)
        return db.applications.find_one({'_id': app_id})
    
    @staticmethod
    def get_by_name(db, name):
        """Get application by name"""
        return db.applications.find_one({'name': name})
    
    @staticmethod
    def update(db, app_id, update_data):
        """Update application information"""
        if isinstance(app_id, str):
            app_id = ObjectId(app_id)
        
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.applications.update_one(
            {'_id': app_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_environment(db, app_id, environment, env_data):
        """Update specific environment configuration"""
        if isinstance(app_id, str):
            app_id = ObjectId(app_id)
        
        if environment not in ['development', 'staging', 'production']:
            raise ValueError("Invalid environment")
        
        update_fields = {}
        for key, value in env_data.items():
            update_fields[f'environments.{environment}.{key}'] = value
        
        update_fields['updated_at'] = datetime.utcnow()
        
        result = db.applications.update_one(
            {'_id': app_id},
            {'$set': update_fields}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_health_status(db, app_id, environment, health_status):
        """Update health status for an environment"""
        return Application.update_environment(
            db, app_id, environment, {'health_status': health_status}
        )
    
    @staticmethod
    def increment_deployment_count(db, app_id, success=True):
        """Increment deployment counters"""
        if isinstance(app_id, str):
            app_id = ObjectId(app_id)
        
        increment_fields = {'metadata.total_deployments': 1}
        if success:
            increment_fields['metadata.successful_deployments'] = 1
        else:
            increment_fields['metadata.failed_deployments'] = 1
        
        result = db.applications.update_one(
            {'_id': app_id},
            {
                '$inc': increment_fields,
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(db, app_id):
        """Delete application (archive it)"""
        if isinstance(app_id, str):
            app_id = ObjectId(app_id)
        
        result = db.applications.update_one(
            {'_id': app_id},
            {'$set': {'status': 'archived', 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def list_all(db, skip=0, limit=50, status=None, language=None):
        """List all applications with pagination and filters"""
        query = {}
        if status:
            query['status'] = status
        if language:
            query['language'] = language
        
        apps = list(db.applications.find(query).skip(skip).limit(limit).sort('created_at', -1))
        total = db.applications.count_documents(query)
        
        return {
            'applications': apps,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def search(db, search_term):
        """Search applications by name or description"""
        query = {
            '$or': [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'description': {'$regex': search_term, '$options': 'i'}},
                {'tags': {'$in': [search_term]}}
            ]
        }
        return list(db.applications.find(query))
    
    @staticmethod
    def get_stats(db):
        """Get application statistics"""
        total = db.applications.count_documents({})
        active = db.applications.count_documents({'status': 'active'})
        inactive = db.applications.count_documents({'status': 'inactive'})
        
        # Get language distribution
        pipeline = [
            {'$group': {'_id': '$language', 'count': {'$sum': 1}}}
        ]
        language_dist = list(db.applications.aggregate(pipeline))
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'language_distribution': language_dist
        }