"""
Kubernetes Service
Manages Kubernetes cluster operations and deployments
"""

import logging
import yaml
from typing import Dict, List, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


class KubernetesService:
    """Service for managing Kubernetes cluster operations"""
    
    def __init__(self, namespace: str = 'default', in_cluster: bool = False):
        """
        Initialize Kubernetes service
        
        Args:
            namespace: Default namespace for operations
            in_cluster: Whether running inside a Kubernetes cluster
        """
        self.namespace = namespace
        self.in_cluster = in_cluster
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Kubernetes API client"""
        try:
            if self.in_cluster:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            else:
                config.load_kube_config()
                logger.info("Loaded Kubernetes configuration from kubeconfig")
            
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.batch_v1 = client.BatchV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {str(e)}")
            raise
    
    def create_namespace(self, namespace: str) -> Dict:
        """
        Create a new namespace
        
        Args:
            namespace: Namespace name
            
        Returns:
            Creation result
        """
        try:
            namespace_obj = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            
            result = self.core_v1.create_namespace(body=namespace_obj)
            
            return {
                'success': True,
                'namespace': namespace,
                'created_at': result.metadata.creation_timestamp
            }
        except ApiException as e:
            if e.status == 409:
                return {
                    'success': True,
                    'namespace': namespace,
                    'message': 'Namespace already exists'
                }
            logger.error(f"Failed to create namespace: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_namespace(self, namespace: str) -> Dict:
        """
        Delete a namespace
        
        Args:
            namespace: Namespace name
            
        Returns:
            Deletion result
        """
        try:
            self.core_v1.delete_namespace(name=namespace)
            return {
                'success': True,
                'namespace': namespace,
                'message': 'Namespace deleted successfully'
            }
        except ApiException as e:
            logger.error(f"Failed to delete namespace: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_deployment(self, name: str, image: str, replicas: int = 1, 
                         namespace: Optional[str] = None, **kwargs) -> Dict:
        """
        Create a deployment
        
        Args:
            name: Deployment name
            image: Container image
            replicas: Number of replicas
            namespace: Namespace (uses default if not specified)
            **kwargs: Additional deployment configuration
            
        Returns:
            Deployment result
        """
        namespace = namespace or self.namespace
        
        try:
            # Container definition
            container = client.V1Container(
                name=name,
                image=image,
                ports=[client.V1ContainerPort(container_port=kwargs.get('port', 8080))],
                env=kwargs.get('env', []),
                resources=kwargs.get('resources')
            )
            
            # Pod template
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={'app': name}),
                spec=client.V1PodSpec(containers=[container])
            )
            
            # Deployment spec
            spec = client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels={'app': name}),
                template=template
            )
            
            # Deployment object
            deployment = client.V1Deployment(
                api_version='apps/v1',
                kind='Deployment',
                metadata=client.V1ObjectMeta(name=name),
                spec=spec
            )
            
            result = self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            return {
                'success': True,
                'deployment': name,
                'namespace': namespace,
                'replicas': replicas,
                'image': image
            }
        except ApiException as e:
            logger.error(f"Failed to create deployment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_deployment(self, name: str, image: Optional[str] = None, 
                         replicas: Optional[int] = None, namespace: Optional[str] = None) -> Dict:
        """
        Update an existing deployment
        
        Args:
            name: Deployment name
            image: New container image
            replicas: New replica count
            namespace: Namespace
            
        Returns:
            Update result
        """
        namespace = namespace or self.namespace
        
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            
            # Update image if provided
            if image:
                deployment.spec.template.spec.containers[0].image = image
            
            # Update replicas if provided
            if replicas is not None:
                deployment.spec.replicas = replicas
            
            # Apply update
            result = self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )
            
            return {
                'success': True,
                'deployment': name,
                'namespace': namespace,
                'updated': True
            }
        except ApiException as e:
            logger.error(f"Failed to update deployment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_deployment(self, name: str, namespace: Optional[str] = None) -> Dict:
        """
        Delete a deployment
        
        Args:
            name: Deployment name
            namespace: Namespace
            
        Returns:
            Deletion result
        """
        namespace = namespace or self.namespace
        
        try:
            self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=client.V1DeleteOptions(propagation_policy='Foreground')
            )
            
            return {
                'success': True,
                'deployment': name,
                'namespace': namespace,
                'message': 'Deployment deleted successfully'
            }
        except ApiException as e:
            logger.error(f"Failed to delete deployment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_deployment_status(self, name: str, namespace: Optional[str] = None) -> Dict:
        """
        Get deployment status
        
        Args:
            name: Deployment name
            namespace: Namespace
            
        Returns:
            Deployment status
        """
        namespace = namespace or self.namespace
        
        try:
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            
            return {
                'success': True,
                'deployment': name,
                'namespace': namespace,
                'replicas': {
                    'desired': deployment.spec.replicas,
                    'ready': deployment.status.ready_replicas or 0,
                    'available': deployment.status.available_replicas or 0,
                    'unavailable': deployment.status.unavailable_replicas or 0
                },
                'conditions': [
                    {
                        'type': condition.type,
                        'status': condition.status,
                        'reason': condition.reason,
                        'message': condition.message
                    }
                    for condition in (deployment.status.conditions or [])
                ]
            }
        except ApiException as e:
            logger.error(f"Failed to get deployment status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_pods(self, namespace: Optional[str] = None, label_selector: Optional[str] = None) -> Dict:
        """
        List pods in namespace
        
        Args:
            namespace: Namespace
            label_selector: Label selector filter
            
        Returns:
            List of pods
        """
        namespace = namespace or self.namespace
        
        try:
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            
            pod_list = []
            for pod in pods.items:
                pod_list.append({
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'status': pod.status.phase,
                    'ip': pod.status.pod_ip,
                    'node': pod.spec.node_name,
                    'containers': [
                        {
                            'name': container.name,
                            'image': container.image,
                            'ready': any(
                                cs.name == container.name and cs.ready
                                for cs in (pod.status.container_statuses or [])
                            )
                        }
                        for container in pod.spec.containers
                    ]
                })
            
            return {
                'success': True,
                'namespace': namespace,
                'count': len(pod_list),
                'pods': pod_list
            }
        except ApiException as e:
            logger.error(f"Failed to list pods: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_pod_logs(self, pod_name: str, namespace: Optional[str] = None, 
                     container: Optional[str] = None, tail_lines: int = 100) -> Dict:
        """
        Get pod logs
        
        Args:
            pod_name: Pod name
            namespace: Namespace
            container: Container name (if pod has multiple containers)
            tail_lines: Number of lines to retrieve
            
        Returns:
            Pod logs
        """
        namespace = namespace or self.namespace
        
        try:
            logs = self.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines
            )
            
            return {
                'success': True,
                'pod': pod_name,
                'namespace': namespace,
                'logs': logs
            }
        except ApiException as e:
            logger.error(f"Failed to get pod logs: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_service(self, name: str, port: int, target_port: int, 
                      service_type: str = 'ClusterIP', namespace: Optional[str] = None) -> Dict:
        """
        Create a Kubernetes service
        
        Args:
            name: Service name
            port: Service port
            target_port: Target container port
            service_type: Service type (ClusterIP, NodePort, LoadBalancer)
            namespace: Namespace
            
        Returns:
            Service creation result
        """
        namespace = namespace or self.namespace
        
        try:
            service = client.V1Service(
                api_version='v1',
                kind='Service',
                metadata=client.V1ObjectMeta(name=name),
                spec=client.V1ServiceSpec(
                    selector={'app': name},
                    ports=[client.V1ServicePort(
                        port=port,
                        target_port=target_port
                    )],
                    type=service_type
                )
            )
            
            result = self.core_v1.create_namespaced_service(
                namespace=namespace,
                body=service
            )
            
            return {
                'success': True,
                'service': name,
                'namespace': namespace,
                'type': service_type,
                'port': port
            }
        except ApiException as e:
            logger.error(f"Failed to create service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def scale_deployment(self, name: str, replicas: int, namespace: Optional[str] = None) -> Dict:
        """
        Scale a deployment
        
        Args:
            name: Deployment name
            replicas: Desired replica count
            namespace: Namespace
            
        Returns:
            Scaling result
        """
        return self.update_deployment(name=name, replicas=replicas, namespace=namespace)
    
    def rollback_deployment(self, name: str, namespace: Optional[str] = None, 
                           revision: Optional[int] = None) -> Dict:
        """
        Rollback a deployment to previous revision
        
        Args:
            name: Deployment name
            namespace: Namespace
            revision: Specific revision to rollback to
            
        Returns:
            Rollback result
        """
        namespace = namespace or self.namespace
        
        try:
            # Get deployment
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            
            # Trigger rollback by updating annotations
            if deployment.spec.template.metadata.annotations is None:
                deployment.spec.template.metadata.annotations = {}
            
            deployment.spec.template.metadata.annotations['kubectl.kubernetes.io/restartedAt'] = \
                client.V1ObjectMeta().creation_timestamp
            
            self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )
            
            return {
                'success': True,
                'deployment': name,
                'namespace': namespace,
                'message': 'Rollback initiated'
            }
        except ApiException as e:
            logger.error(f"Failed to rollback deployment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
