"""
Monitoring Service
Collects and manages system metrics, health checks, and alerts
"""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import psutil

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for monitoring system health and metrics"""
    
    def __init__(self, prometheus_url: Optional[str] = None):
        """
        Initialize monitoring service
        
        Args:
            prometheus_url: Prometheus server URL
        """
        self.prometheus_url = prometheus_url or 'http://localhost:9090'
    
    def get_system_metrics(self) -> Dict:
        """
        Get current system metrics
        
        Returns:
            System metrics including CPU, memory, disk
        """
        try:
            metrics = {
                'cpu': {
                    'percent': psutil.cpu_percent(interval=1),
                    'count': psutil.cpu_count(),
                    'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent,
                    'used': psutil.virtual_memory().used
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'network': {
                    'bytes_sent': psutil.net_io_counters().bytes_sent,
                    'bytes_recv': psutil.net_io_counters().bytes_recv,
                    'packets_sent': psutil.net_io_counters().packets_sent,
                    'packets_recv': psutil.net_io_counters().packets_recv
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_prometheus(self, query: str, time: Optional[str] = None) -> Dict:
        """
        Query Prometheus for metrics
        
        Args:
            query: PromQL query
            time: Query time (RFC3339 or Unix timestamp)
            
        Returns:
            Query results
        """
        try:
            url = f'{self.prometheus_url}/api/v1/query'
            params = {'query': query}
            
            if time:
                params['time'] = time
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': data['status'] == 'success',
                'data': data.get('data', {}),
                'query': query
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Prometheus query failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_prometheus_range(self, query: str, start: str, end: str, step: str = '15s') -> Dict:
        """
        Query Prometheus for range of metrics
        
        Args:
            query: PromQL query
            start: Start time
            end: End time
            step: Query resolution step
            
        Returns:
            Range query results
        """
        try:
            url = f'{self.prometheus_url}/api/v1/query_range'
            params = {
                'query': query,
                'start': start,
                'end': end,
                'step': step
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': data['status'] == 'success',
                'data': data.get('data', {}),
                'query': query
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Prometheus range query failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_application_metrics(self, app_name: str, time_range: str = '1h') -> Dict:
        """
        Get metrics for a specific application
        
        Args:
            app_name: Application name
            time_range: Time range (1h, 24h, 7d, etc.)
            
        Returns:
            Application metrics
        """
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            
            if time_range.endswith('h'):
                hours = int(time_range[:-1])
                start_time = end_time - timedelta(hours=hours)
            elif time_range.endswith('d'):
                days = int(time_range[:-1])
                start_time = end_time - timedelta(days=days)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Query various metrics
            metrics = {}
            
            # CPU usage
            cpu_query = f'rate(container_cpu_usage_seconds_total{{app="{app_name}"}}[5m])'
            cpu_result = self.query_prometheus_range(
                cpu_query,
                start_time.isoformat(),
                end_time.isoformat()
            )
            if cpu_result['success']:
                metrics['cpu'] = cpu_result['data']
            
            # Memory usage
            memory_query = f'container_memory_usage_bytes{{app="{app_name}"}}'
            memory_result = self.query_prometheus_range(
                memory_query,
                start_time.isoformat(),
                end_time.isoformat()
            )
            if memory_result['success']:
                metrics['memory'] = memory_result['data']
            
            # Request rate
            request_query = f'rate(http_requests_total{{app="{app_name}"}}[5m])'
            request_result = self.query_prometheus_range(
                request_query,
                start_time.isoformat(),
                end_time.isoformat()
            )
            if request_result['success']:
                metrics['requests'] = request_result['data']
            
            return {
                'success': True,
                'application': app_name,
                'time_range': time_range,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Failed to get application metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_health(self, endpoint: str, timeout: int = 5) -> Dict:
        """
        Check health of an endpoint
        
        Args:
            endpoint: Health check endpoint URL
            timeout: Request timeout in seconds
            
        Returns:
            Health check result
        """
        try:
            start_time = datetime.utcnow()
            response = requests.get(endpoint, timeout=timeout)
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds() * 1000  # ms
            
            return {
                'success': True,
                'healthy': response.status_code == 200,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'endpoint': endpoint,
                'timestamp': end_time.isoformat()
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'healthy': False,
                'error': 'Health check timed out',
                'endpoint': endpoint
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'healthy': False,
                'error': str(e),
                'endpoint': endpoint
            }
    
    def create_alert(self, alert_config: Dict) -> Dict:
        """
        Create a monitoring alert
        
        Args:
            alert_config: Alert configuration
            
        Returns:
            Alert creation result
        """
        try:
            alert = {
                'id': alert_config.get('id') or f"alert-{datetime.utcnow().timestamp()}",
                'name': alert_config.get('name'),
                'severity': alert_config.get('severity', 'warning'),
                'condition': alert_config.get('condition'),
                'threshold': alert_config.get('threshold'),
                'status': 'active',
                'created_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'alert': alert
            }
        except Exception as e:
            logger.error(f"Failed to create alert: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def evaluate_alert(self, alert: Dict, current_value: float) -> Dict:
        """
        Evaluate if alert condition is met
        
        Args:
            alert: Alert configuration
            current_value: Current metric value
            
        Returns:
            Evaluation result
        """
        try:
            threshold = alert.get('threshold', 0)
            condition = alert.get('condition', 'greater_than')
            
            triggered = False
            
            if condition == 'greater_than':
                triggered = current_value > threshold
            elif condition == 'less_than':
                triggered = current_value < threshold
            elif condition == 'equals':
                triggered = current_value == threshold
            elif condition == 'not_equals':
                triggered = current_value != threshold
            
            return {
                'success': True,
                'alert_id': alert.get('id'),
                'triggered': triggered,
                'current_value': current_value,
                'threshold': threshold,
                'condition': condition
            }
        except Exception as e:
            logger.error(f"Failed to evaluate alert: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_service_status(self, services: List[str]) -> Dict:
        """
        Get status of multiple services
        
        Args:
            services: List of service names/endpoints
            
        Returns:
            Status of all services
        """
        try:
            statuses = {}
            
            for service in services:
                # Assume service is a URL endpoint
                health_result = self.check_health(service)
                statuses[service] = {
                    'healthy': health_result.get('healthy', False),
                    'response_time_ms': health_result.get('response_time_ms'),
                    'status_code': health_result.get('status_code')
                }
            
            all_healthy = all(status['healthy'] for status in statuses.values())
            
            return {
                'success': True,
                'overall_status': 'healthy' if all_healthy else 'unhealthy',
                'services': statuses,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get service status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def collect_metrics_snapshot(self) -> Dict:
        """
        Collect a complete snapshot of all metrics
        
        Returns:
            Complete metrics snapshot
        """
        try:
            system_metrics = self.get_system_metrics()
            
            snapshot = {
                'timestamp': datetime.utcnow().isoformat(),
                'system': system_metrics.get('metrics', {}),
                'uptime': psutil.boot_time(),
                'process_count': len(psutil.pids())
            }
            
            return {
                'success': True,
                'snapshot': snapshot
            }
        except Exception as e:
            logger.error(f"Failed to collect metrics snapshot: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }