"""
Incident Detector Service
Analyzes health check results and creates incidents
"""
import os
from pymongo import MongoClient
from datetime import datetime
from health_checker import HealthChecker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncidentDetector:
    def __init__(self):
        # MongoDB connection
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/capx_platform')
        self.client = MongoClient(mongo_uri)
        self.db = self.client.capx_platform
        
        # Health checker
        self.health_checker = HealthChecker()
    
    def analyze_and_create_incidents(self, namespace='capx-platform'):
        """Analyze health check results and create incidents"""
        logger.info("Running health checks...")
        
        health_results = self.health_checker.run_health_checks(namespace)
        
        if health_results['overall_status'] == 'unhealthy':
            logger.warning("Unhealthy state detected, creating incidents...")
            
            # Process pod issues
            for issue in health_results['checks']['pods']['issues']:
                self._create_incident_from_pod_issue(issue, namespace)
            
            # Process deployment issues
            for issue in health_results['checks']['deployments']['issues']:
                self._create_incident_from_deployment_issue(issue, namespace)
            
            # Process service issues
            for issue in health_results['checks']['services']['issues']:
                self._create_incident_from_service_issue(issue, namespace)
    
    def _create_incident_from_pod_issue(self, issue, namespace):
        """Create incident from pod health issue"""
        pod_name = issue.get('pod_name')
        issue_type = issue.get('issue')
        
        # Check if incident already exists for this pod
        existing = self.db.incidents.find_one({
            'application_name': pod_name.split('-')[0],  # Extract app name from pod
            'status': {'$in': ['open', 'investigating']},
            'incident_type': issue_type
        })
        
        if existing:
            logger.info(f"Incident already exists for {pod_name} - {issue_type}")
            return
        
        # Map issue type to severity
        severity_map = {
            'crash_loop': 'critical',
            'high_restart_count': 'high',
            'container_not_ready': 'medium',
            'not_running': 'high'
        }
        
        severity = severity_map.get(issue_type, 'medium')
        
        # Get application info
        app_name = pod_name.split('-')[0]
        app = self.db.applications.find_one({'name': app_name})
        
        incident = {
            'application_id': str(app['_id']) if app else None,
            'application_name': app_name,
            'environment': namespace,
            'title': f"Pod health issue: {issue_type}",
            'description': f"Pod {pod_name} is experiencing {issue_type}",
            'severity': severity,
            'status': 'open',
            'incident_type': issue_type,
            'detected_by': 'auto_monitoring',
            'affected_components': [pod_name],
            'metrics_snapshot': issue,
            'auto_healing': {
                'attempted': False,
                'success': None,
                'actions_taken': []
            },
            'timeline': [
                {
                    'timestamp': datetime.utcnow(),
                    'event': 'Incident detected',
                    'actor': 'incident_detector',
                    'details': str(issue)
                }
            ],
            'root_cause': None,
            'resolution': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.db.incidents.insert_one(incident)
        logger.info(f"Created incident {result.inserted_id} for {pod_name}")
        
        # Update application incident count
        if app:
            self.db.applications.update_one(
                {'_id': app['_id']},
                {
                    '$inc': {'metadata.total_incidents': 1},
                    '$set': {'metadata.last_incident': datetime.utcnow()}
                }
            )
    
    def _create_incident_from_deployment_issue(self, issue, namespace):
        """Create incident from deployment health issue"""
        deployment_name = issue.get('deployment_name')
        issue_type = issue.get('issue')
        
        # Check if incident already exists
        existing = self.db.incidents.find_one({
            'application_name': deployment_name,
            'status': {'$in': ['open', 'investigating']},
            'incident_type': issue_type
        })
        
        if existing:
            logger.info(f"Incident already exists for {deployment_name} - {issue_type}")
            return
        
        severity = 'high' if issue_type == 'insufficient_replicas' else 'medium'
        
        app = self.db.applications.find_one({'name': deployment_name})
        
        incident = {
            'application_id': str(app['_id']) if app else None,
            'application_name': deployment_name,
            'environment': namespace,
            'title': f"Deployment issue: {issue_type}",
            'description': f"Deployment {deployment_name} is experiencing {issue_type}",
            'severity': severity,
            'status': 'open',
            'incident_type': issue_type,
            'detected_by': 'auto_monitoring',
            'affected_components': [deployment_name],
            'metrics_snapshot': issue,
            'auto_healing': {
                'attempted': False,
                'success': None,
                'actions_taken': []
            },
            'timeline': [
                {
                    'timestamp': datetime.utcnow(),
                    'event': 'Incident detected',
                    'actor': 'incident_detector',
                    'details': str(issue)
                }
            ],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.db.incidents.insert_one(incident)
        logger.info(f"Created incident {result.inserted_id} for {deployment_name}")
        
        if app:
            self.db.applications.update_one(
                {'_id': app['_id']},
                {
                    '$inc': {'metadata.total_incidents': 1},
                    '$set': {'metadata.last_incident': datetime.utcnow()}
                }
            )
    
    def _create_incident_from_service_issue(self, issue, namespace):
        """Create incident from service health issue"""
        service_name = issue.get('service_name')
        issue_type = issue.get('issue')
        
        existing = self.db.incidents.find_one({
            'application_name': service_name,
            'status': {'$in': ['open', 'investigating']},
            'incident_type': issue_type
        })
        
        if existing:
            logger.info(f"Incident already exists for {service_name} - {issue_type}")
            return
        
        app = self.db.applications.find_one({'name': service_name.replace('-service', '')})
        
        incident = {
            'application_id': str(app['_id']) if app else None,
            'application_name': service_name,
            'environment': namespace,
            'title': f"Service issue: {issue_type}",
            'description': f"Service {service_name} is experiencing {issue_type}",
            'severity': 'high',
            'status': 'open',
            'incident_type': issue_type,
            'detected_by': 'auto_monitoring',
            'affected_components': [service_name],
            'metrics_snapshot': issue,
            'auto_healing': {
                'attempted': False,
                'success': None,
                'actions_taken': []
            },
            'timeline': [
                {
                    'timestamp': datetime.utcnow(),
                    'event': 'Incident detected',
                    'actor': 'incident_detector',
                    'details': str(issue)
                }
            ],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.db.incidents.insert_one(incident)
        logger.info(f"Created incident {result.inserted_id} for {service_name}")
        
        if app:
            self.db.applications.update_one(
                {'_id': app['_id']},
                {
                    '$inc': {'metadata.total_incidents': 1},
                    '$set': {'metadata.last_incident': datetime.utcnow()}
                }
            )


if __name__ == '__main__':
    import time
    
    logger.info("Starting Incident Detector...")
    
    detector = IncidentDetector()
    check_interval = int(os.getenv('INCIDENT_CHECK_INTERVAL', '60'))
    
    while True:
        try:
            detector.analyze_and_create_incidents()
            logger.info(f"Sleeping for {check_interval} seconds...")
            time.sleep(check_interval)
        except Exception as e:
            logger.error(f"Error in incident detector: {e}")
            time.sleep(30)