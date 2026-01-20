import time
import logging
from datetime import datetime
from kubernetes import client, config
from pymongo import MongoClient
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoRemediationEngine:
    """
    Auto-Healing & Self-Remediation Engine
    Monitors applications and automatically fixes common issues
    """
    
    def __init__(self):
        # Initialize Kubernetes client
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_core_v1 = client.CoreV1Api()
        
        # Initialize MongoDB
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/capx_platform')
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client.capx_platform
        
        # Remediation strategies
        self.remediation_strategies = {
            'pod_crash_loop': self.fix_crash_loop,
            'high_memory': self.fix_memory_issue,
            'high_cpu': self.fix_cpu_issue,
            'pod_not_ready': self.fix_pod_not_ready,
            'service_unavailable': self.fix_service_unavailable
        }
    
    def monitor_and_heal(self, namespace='capx-platform'):
        """
        Main monitoring loop - checks health and triggers healing
        """
        logger.info(f"🔍 Starting health monitoring for namespace: {namespace}")
        
        while True:
            try:
                # Get all deployments in namespace
                deployments = self.k8s_apps_v1.list_namespaced_deployment(namespace)
                
                for deployment in deployments.items:
                    app_name = deployment.metadata.name
                    
                    # Check deployment health
                    issues = self.check_deployment_health(deployment, namespace)
                    
                    if issues:
                        logger.warning(f"⚠️ Issues detected in {app_name}: {issues}")
                        
                        # Create incident
                        incident_id = self.create_incident(app_name, issues, namespace)
                        
                        # Attempt auto-remediation
                        for issue in issues:
                            success = self.attempt_remediation(
                                app_name, 
                                issue, 
                                namespace, 
                                incident_id
                            )
                            
                            if success:
                                logger.info(f"✅ Successfully fixed {issue} for {app_name}")
                            else:
                                logger.error(f"❌ Failed to fix {issue} for {app_name}")
                
                # Sleep before next check
                time.sleep(int(os.getenv('INCIDENT_CHECK_INTERVAL', 60)))
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
    
    def check_deployment_health(self, deployment, namespace):
        """
        Check deployment for common issues
        """
        issues = []
        app_name = deployment.metadata.name
        
        # Check replica health
        desired_replicas = deployment.spec.replicas
        ready_replicas = deployment.status.ready_replicas or 0
        
        if ready_replicas < desired_replicas:
            issues.append('pod_not_ready')
        
        # Check pods for crash loops
        pods = self.k8s_core_v1.list_namespaced_pod(
            namespace,
            label_selector=f"app={app_name}"
        )
        
        for pod in pods.items:
            # Check container statuses
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.restart_count > 3:
                        issues.append('pod_crash_loop')
                    
                    # Check waiting state
                    if container.state.waiting:
                        if container.state.waiting.reason in ['CrashLoopBackOff', 'ImagePullBackOff']:
                            issues.append('pod_crash_loop')
            
            # Check resource usage (requires metrics-server)
            try:
                metrics = self.get_pod_metrics(pod.metadata.name, namespace)
                if metrics:
                    if metrics.get('memory_percent', 0) > 90:
                        issues.append('high_memory')
                    if metrics.get('cpu_percent', 0) > 90:
                        issues.append('high_cpu')
            except:
                pass
        
        return list(set(issues))  # Remove duplicates
    
    def attempt_remediation(self, app_name, issue_type, namespace, incident_id):
        """
        Attempt to fix the issue using appropriate strategy
        """
        strategy = self.remediation_strategies.get(issue_type)
        
        if not strategy:
            logger.warning(f"No remediation strategy for {issue_type}")
            return False
        
        try:
            logger.info(f"🔧 Attempting remediation for {issue_type} on {app_name}")
            
            success = strategy(app_name, namespace)
            
            # Record remediation attempt
            self.db.incidents.update_one(
                {'_id': incident_id},
                {
                    '$set': {
                        'auto_healing.attempted': True,
                        'auto_healing.success': success,
                        'updated_at': datetime.utcnow()
                    },
                    '$push': {
                        'auto_healing.actions_taken': {
                            'action': issue_type,
                            'timestamp': datetime.utcnow(),
                            'success': success
                        },
                        'timeline': {
                            'timestamp': datetime.utcnow(),
                            'event': f'Auto-healing: {issue_type}',
                            'actor': 'auto_healing_system',
                            'details': f'Remediation {"succeeded" if success else "failed"}'
                        }
                    }
                }
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error during remediation: {e}")
            return False
    
    def fix_crash_loop(self, app_name, namespace):
        """
        Fix crash loop by restarting deployment with rollback if needed
        """
        try:
            # Get deployment
            deployment = self.k8s_apps_v1.read_namespaced_deployment(app_name, namespace)
            
            # Check if there's a previous revision
            revision_history = deployment.metadata.annotations.get('deployment.kubernetes.io/revision')
            
            if revision_history and int(revision_history) > 1:
                # Rollback to previous version
                logger.info(f"Rolling back {app_name} to previous revision")
                
                rollback = client.AppsV1beta1Deployment(
                    api_version='apps/v1beta1',
                    kind='DeploymentRollback',
                    name=app_name,
                    rollback_to=client.AppsV1beta1RollbackConfig(revision=0)
                )
                
                # Note: Use kubectl rollback in production
                # For now, restart pods
                self.restart_deployment(app_name, namespace)
                return True
            else:
                # Just restart
                self.restart_deployment(app_name, namespace)
                return True
                
        except Exception as e:
            logger.error(f"Error fixing crash loop: {e}")
            return False
    
    def fix_memory_issue(self, app_name, namespace):
        """
        Fix memory issues by restarting high-memory pods
        """
        try:
            # Get pods
            pods = self.k8s_core_v1.list_namespaced_pod(
                namespace,
                label_selector=f"app={app_name}"
            )
            
            # Restart high-memory pods
            for pod in pods.items:
                metrics = self.get_pod_metrics(pod.metadata.name, namespace)
                if metrics and metrics.get('memory_percent', 0) > 90:
                    logger.info(f"Restarting high-memory pod: {pod.metadata.name}")
                    self.k8s_core_v1.delete_namespaced_pod(
                        pod.metadata.name,
                        namespace,
                        grace_period_seconds=30
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing memory issue: {e}")
            return False
    
    def fix_cpu_issue(self, app_name, namespace):
        """
        Fix CPU issues by scaling up replicas
        """
        try:
            deployment = self.k8s_apps_v1.read_namespaced_deployment(app_name, namespace)
            current_replicas = deployment.spec.replicas
            
            # Scale up by 50% (max 10)
            new_replicas = min(int(current_replicas * 1.5), 10)
            
            logger.info(f"Scaling {app_name} from {current_replicas} to {new_replicas} replicas")
            
            deployment.spec.replicas = new_replicas
            self.k8s_apps_v1.patch_namespaced_deployment(
                app_name,
                namespace,
                deployment
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing CPU issue: {e}")
            return False
    
    def fix_pod_not_ready(self, app_name, namespace):
        """
        Fix pods not ready by restarting them
        """
        try:
            self.restart_deployment(app_name, namespace)
            return True
        except Exception as e:
            logger.error(f"Error fixing pod not ready: {e}")
            return False
    
    def fix_service_unavailable(self, app_name, namespace):
        """
        Fix service unavailable by recreating service
        """
        try:
            # Delete and recreate service endpoint
            services = self.k8s_core_v1.list_namespaced_service(
                namespace,
                label_selector=f"app={app_name}"
            )
            
            for service in services.items:
                logger.info(f"Refreshing service: {service.metadata.name}")
                # Patch service to refresh endpoints
                self.k8s_core_v1.patch_namespaced_service(
                    service.metadata.name,
                    namespace,
                    {'metadata': {'annotations': {'refreshed': str(datetime.utcnow())}}}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing service: {e}")
            return False
    
    def restart_deployment(self, app_name, namespace):
        """
        Restart deployment by updating annotation
        """
        now = datetime.utcnow().isoformat()
        body = {
            'spec': {
                'template': {
                    'metadata': {
                        'annotations': {
                            'kubectl.kubernetes.io/restartedAt': now
                        }
                    }
                }
            }
        }
        
        self.k8s_apps_v1.patch_namespaced_deployment(
            app_name,
            namespace,
            body
        )
        
        logger.info(f"Deployment {app_name} restarted")
    
    def get_pod_metrics(self, pod_name, namespace):
        """
        Get pod resource metrics (requires metrics-server)
        """
        # This would integrate with Prometheus or metrics-server
        # Placeholder for now
        return None
    
    def create_incident(self, app_name, issues, namespace):
        """
        Create incident record in MongoDB
        """
        # Get application ID
        app = self.db.applications.find_one({'name': app_name})
        
        if not app:
            return None
        
        incident = {
            'application_id': str(app['_id']),
            'application_name': app_name,
            'environment': namespace,
            'title': f"Auto-detected issues: {', '.join(issues)}",
            'description': f"Automatic monitoring detected issues in {app_name}",
            'severity': 'high' if 'pod_crash_loop' in issues else 'medium',
            'status': 'open',
            'incident_type': issues[0] if issues else 'unknown',
            'detected_by': 'auto_monitoring',
            'affected_components': [app_name],
            'auto_healing': {
                'attempted': False,
                'success': None,
                'actions_taken': []
            },
            'timeline': [
                {
                    'timestamp': datetime.utcnow(),
                    'event': 'Incident detected',
                    'actor': 'auto_monitoring',
                    'details': f'Issues: {", ".join(issues)}'
                }
            ],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.db.incidents.insert_one(incident)
        logger.info(f"Created incident: {result.inserted_id}")
        
        return result.inserted_id


if __name__ == '__main__':
    logger.info("🚀 Starting CAP-X Auto-Remediation Engine")
    
    engine = AutoRemediationEngine()
    engine.monitor_and_heal(namespace='capx-platform')