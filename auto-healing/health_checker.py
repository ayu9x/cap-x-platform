"""
Health Checker Service
Monitors application health and detects issues
"""
import time
import requests
from kubernetes import client, config
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    def check_pod_health(self, namespace='capx-platform'):
        """Check health of all pods in namespace"""
        unhealthy_pods = []
        
        try:
            pods = self.core_v1.list_namespaced_pod(namespace)
            
            for pod in pods.items:
                pod_name = pod.metadata.name
                
                # Check pod phase
                if pod.status.phase not in ['Running', 'Succeeded']:
                    unhealthy_pods.append({
                        'pod_name': pod_name,
                        'issue': 'not_running',
                        'phase': pod.status.phase,
                        'reason': pod.status.reason
                    })
                    continue
                
                # Check container statuses
                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        # Check restart count
                        if container.restart_count > 3:
                            unhealthy_pods.append({
                                'pod_name': pod_name,
                                'issue': 'high_restart_count',
                                'restart_count': container.restart_count,
                                'container': container.name
                            })
                        
                        # Check if container is ready
                        if not container.ready:
                            unhealthy_pods.append({
                                'pod_name': pod_name,
                                'issue': 'container_not_ready',
                                'container': container.name
                            })
                        
                        # Check for crash loop
                        if container.state.waiting:
                            if container.state.waiting.reason in ['CrashLoopBackOff', 'ImagePullBackOff']:
                                unhealthy_pods.append({
                                    'pod_name': pod_name,
                                    'issue': 'crash_loop',
                                    'reason': container.state.waiting.reason,
                                    'message': container.state.waiting.message
                                })
            
            return unhealthy_pods
            
        except Exception as e:
            logger.error(f"Error checking pod health: {e}")
            return []
    
    def check_deployment_health(self, namespace='capx-platform'):
        """Check health of deployments"""
        unhealthy_deployments = []
        
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace)
            
            for deployment in deployments.items:
                name = deployment.metadata.name
                desired = deployment.spec.replicas
                ready = deployment.status.ready_replicas or 0
                
                # Check if deployment has enough ready replicas
                if ready < desired:
                    unhealthy_deployments.append({
                        'deployment_name': name,
                        'issue': 'insufficient_replicas',
                        'desired': desired,
                        'ready': ready,
                        'missing': desired - ready
                    })
                
                # Check if deployment is progressing
                if deployment.status.conditions:
                    for condition in deployment.status.conditions:
                        if condition.type == 'Progressing' and condition.status == 'False':
                            unhealthy_deployments.append({
                                'deployment_name': name,
                                'issue': 'not_progressing',
                                'reason': condition.reason,
                                'message': condition.message
                            })
            
            return unhealthy_deployments
            
        except Exception as e:
            logger.error(f"Error checking deployment health: {e}")
            return []
    
    def check_service_endpoints(self, namespace='capx-platform'):
        """Check if services have healthy endpoints"""
        unhealthy_services = []
        
        try:
            services = self.core_v1.list_namespaced_service(namespace)
            
            for service in services.items:
                service_name = service.metadata.name
                
                # Get endpoints for this service
                try:
                    endpoints = self.core_v1.read_namespaced_endpoints(service_name, namespace)
                    
                    # Check if service has any ready endpoints
                    has_ready_endpoints = False
                    if endpoints.subsets:
                        for subset in endpoints.subsets:
                            if subset.addresses:
                                has_ready_endpoints = True
                                break
                    
                    if not has_ready_endpoints:
                        unhealthy_services.append({
                            'service_name': service_name,
                            'issue': 'no_endpoints',
                            'message': 'Service has no ready endpoints'
                        })
                
                except Exception as e:
                    logger.error(f"Error checking endpoints for {service_name}: {e}")
            
            return unhealthy_services
            
        except Exception as e:
            logger.error(f"Error checking service endpoints: {e}")
            return []
    
    def check_http_endpoint(self, url, timeout=5):
        """Check if HTTP endpoint is responding"""
        try:
            response = requests.get(url, timeout=timeout)
            return {
                'healthy': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
        except requests.exceptions.Timeout:
            return {
                'healthy': False,
                'error': 'timeout',
                'message': f'Request timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': 'connection_error',
                'message': str(e)
            }
    
    def get_pod_logs(self, pod_name, namespace='capx-platform', tail_lines=50):
        """Get recent logs from a pod"""
        try:
            logs = self.core_v1.read_namespaced_pod_log(
                pod_name,
                namespace,
                tail_lines=tail_lines
            )
            return logs
        except Exception as e:
            logger.error(f"Error getting logs for {pod_name}: {e}")
            return None
    
    def run_health_checks(self, namespace='capx-platform'):
        """Run all health checks and return results"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'namespace': namespace,
            'checks': {
                'pods': {
                    'status': 'healthy',
                    'issues': []
                },
                'deployments': {
                    'status': 'healthy',
                    'issues': []
                },
                'services': {
                    'status': 'healthy',
                    'issues': []
                }
            },
            'overall_status': 'healthy'
        }
        
        # Check pods
        pod_issues = self.check_pod_health(namespace)
        if pod_issues:
            results['checks']['pods']['status'] = 'unhealthy'
            results['checks']['pods']['issues'] = pod_issues
            results['overall_status'] = 'unhealthy'
        
        # Check deployments
        deployment_issues = self.check_deployment_health(namespace)
        if deployment_issues:
            results['checks']['deployments']['status'] = 'unhealthy'
            results['checks']['deployments']['issues'] = deployment_issues
            results['overall_status'] = 'unhealthy'
        
        # Check services
        service_issues = self.check_service_endpoints(namespace)
        if service_issues:
            results['checks']['services']['status'] = 'unhealthy'
            results['checks']['services']['issues'] = service_issues
            results['overall_status'] = 'unhealthy'
        
        return results


if __name__ == '__main__':
    logger.info("Starting Health Checker...")
    
    checker = HealthChecker()
    
    while True:
        try:
            results = checker.run_health_checks()
            
            if results['overall_status'] == 'unhealthy':
                logger.warning(f"Health check failed: {results}")
            else:
                logger.info("All health checks passed")
            
            # Sleep for 30 seconds before next check
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in health check loop: {e}")
            time.sleep(30)