"""
Auto-Healing Service
Manages automatic detection and remediation of system issues
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RemediationAction(Enum):
    """Types of remediation actions"""
    RESTART_POD = "restart_pod"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ROLLBACK = "rollback"
    ALERT_ONLY = "alert_only"
    CUSTOM_SCRIPT = "custom_script"


class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AutoHealingService:
    """Service for automatic detection and healing of system issues"""
    
    def __init__(self, kubernetes_service=None, monitoring_service=None):
        """
        Initialize auto-healing service
        
        Args:
            kubernetes_service: KubernetesService instance
            monitoring_service: MonitoringService instance
        """
        self.kubernetes_service = kubernetes_service
        self.monitoring_service = monitoring_service
        self.healing_rules = []
        self.incident_history = []
    
    def add_healing_rule(self, rule: Dict) -> Dict:
        """
        Add a healing rule
        
        Args:
            rule: Healing rule configuration
            
        Returns:
            Rule addition result
        """
        try:
            rule_id = rule.get('id') or f"rule-{len(self.healing_rules) + 1}"
            
            healing_rule = {
                'id': rule_id,
                'name': rule.get('name'),
                'condition': rule.get('condition'),
                'threshold': rule.get('threshold'),
                'action': rule.get('action'),
                'cooldown_minutes': rule.get('cooldown_minutes', 5),
                'max_attempts': rule.get('max_attempts', 3),
                'enabled': rule.get('enabled', True),
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.healing_rules.append(healing_rule)
            
            return {
                'success': True,
                'rule': healing_rule
            }
        except Exception as e:
            logger.error(f"Failed to add healing rule: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_healing_rule(self, rule_id: str) -> Dict:
        """
        Remove a healing rule
        
        Args:
            rule_id: Rule ID to remove
            
        Returns:
            Removal result
        """
        try:
            self.healing_rules = [r for r in self.healing_rules if r['id'] != rule_id]
            
            return {
                'success': True,
                'rule_id': rule_id,
                'message': 'Healing rule removed'
            }
        except Exception as e:
            logger.error(f"Failed to remove healing rule: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_anomaly(self, metric_name: str, current_value: float, 
                      historical_values: List[float]) -> Dict:
        """
        Detect anomalies in metrics using statistical analysis
        
        Args:
            metric_name: Name of the metric
            current_value: Current metric value
            historical_values: Historical values for comparison
            
        Returns:
            Anomaly detection result
        """
        try:
            if not historical_values:
                return {
                    'success': True,
                    'anomaly_detected': False,
                    'reason': 'Insufficient historical data'
                }
            
            # Calculate mean and standard deviation
            mean = sum(historical_values) / len(historical_values)
            variance = sum((x - mean) ** 2 for x in historical_values) / len(historical_values)
            std_dev = variance ** 0.5
            
            # Check if current value is outside 3 standard deviations (99.7% confidence)
            threshold = 3 * std_dev
            deviation = abs(current_value - mean)
            
            is_anomaly = deviation > threshold
            
            return {
                'success': True,
                'metric': metric_name,
                'anomaly_detected': is_anomaly,
                'current_value': current_value,
                'mean': mean,
                'std_dev': std_dev,
                'deviation': deviation,
                'threshold': threshold,
                'severity': self._calculate_severity(deviation, threshold)
            }
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_severity(self, deviation: float, threshold: float) -> str:
        """Calculate incident severity based on deviation"""
        ratio = deviation / threshold if threshold > 0 else 0
        
        if ratio > 2:
            return IncidentSeverity.CRITICAL.value
        elif ratio > 1.5:
            return IncidentSeverity.HIGH.value
        elif ratio > 1:
            return IncidentSeverity.MEDIUM.value
        else:
            return IncidentSeverity.LOW.value
    
    def evaluate_healing_rules(self, metrics: Dict) -> List[Dict]:
        """
        Evaluate all healing rules against current metrics
        
        Args:
            metrics: Current system metrics
            
        Returns:
            List of triggered rules
        """
        triggered_rules = []
        
        try:
            for rule in self.healing_rules:
                if not rule.get('enabled'):
                    continue
                
                condition = rule.get('condition')
                threshold = rule.get('threshold')
                
                # Extract metric value based on condition
                metric_value = self._extract_metric_value(metrics, condition)
                
                if metric_value is None:
                    continue
                
                # Check if threshold is exceeded
                if self._check_threshold(metric_value, threshold, condition):
                    triggered_rules.append({
                        'rule': rule,
                        'current_value': metric_value,
                        'threshold': threshold,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            return triggered_rules
        except Exception as e:
            logger.error(f"Failed to evaluate healing rules: {str(e)}")
            return []
    
    def _extract_metric_value(self, metrics: Dict, condition: str) -> Optional[float]:
        """Extract metric value from metrics dict based on condition"""
        try:
            # Parse condition like "cpu.percent > 80"
            parts = condition.split()
            if len(parts) < 3:
                return None
            
            metric_path = parts[0]
            
            # Navigate nested dict
            value = metrics
            for key in metric_path.split('.'):
                value = value.get(key)
                if value is None:
                    return None
            
            return float(value)
        except Exception:
            return None
    
    def _check_threshold(self, value: float, threshold: float, condition: str) -> bool:
        """Check if value exceeds threshold based on condition"""
        try:
            if '>' in condition:
                return value > threshold
            elif '<' in condition:
                return value < threshold
            elif '=' in condition:
                return value == threshold
            else:
                return False
        except Exception:
            return False
    
    def execute_remediation(self, action: str, target: Dict) -> Dict:
        """
        Execute remediation action
        
        Args:
            action: Remediation action type
            target: Target resource information
            
        Returns:
            Remediation result
        """
        try:
            action_type = RemediationAction(action)
            
            if action_type == RemediationAction.RESTART_POD:
                return self._restart_pod(target)
            elif action_type == RemediationAction.SCALE_UP:
                return self._scale_deployment(target, scale_up=True)
            elif action_type == RemediationAction.SCALE_DOWN:
                return self._scale_deployment(target, scale_up=False)
            elif action_type == RemediationAction.ROLLBACK:
                return self._rollback_deployment(target)
            elif action_type == RemediationAction.ALERT_ONLY:
                return self._create_alert(target)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported action: {action}'
                }
        except Exception as e:
            logger.error(f"Remediation execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _restart_pod(self, target: Dict) -> Dict:
        """Restart a pod"""
        if not self.kubernetes_service:
            return {'success': False, 'error': 'Kubernetes service not available'}
        
        pod_name = target.get('pod_name')
        namespace = target.get('namespace', 'default')
        
        # Delete pod to trigger restart
        result = self.kubernetes_service.core_v1.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace
        )
        
        return {
            'success': True,
            'action': 'restart_pod',
            'pod': pod_name,
            'namespace': namespace
        }
    
    def _scale_deployment(self, target: Dict, scale_up: bool = True) -> Dict:
        """Scale a deployment up or down"""
        if not self.kubernetes_service:
            return {'success': False, 'error': 'Kubernetes service not available'}
        
        deployment_name = target.get('deployment_name')
        namespace = target.get('namespace', 'default')
        current_replicas = target.get('current_replicas', 1)
        
        # Calculate new replica count
        if scale_up:
            new_replicas = current_replicas + 1
        else:
            new_replicas = max(1, current_replicas - 1)
        
        result = self.kubernetes_service.scale_deployment(
            name=deployment_name,
            replicas=new_replicas,
            namespace=namespace
        )
        
        return {
            'success': result.get('success', False),
            'action': 'scale_up' if scale_up else 'scale_down',
            'deployment': deployment_name,
            'old_replicas': current_replicas,
            'new_replicas': new_replicas
        }
    
    def _rollback_deployment(self, target: Dict) -> Dict:
        """Rollback a deployment"""
        if not self.kubernetes_service:
            return {'success': False, 'error': 'Kubernetes service not available'}
        
        deployment_name = target.get('deployment_name')
        namespace = target.get('namespace', 'default')
        
        result = self.kubernetes_service.rollback_deployment(
            name=deployment_name,
            namespace=namespace
        )
        
        return result
    
    def _create_alert(self, target: Dict) -> Dict:
        """Create an alert without taking action"""
        return {
            'success': True,
            'action': 'alert_only',
            'message': f"Alert created for {target.get('resource_name')}",
            'target': target
        }
    
    def create_incident(self, incident_data: Dict) -> Dict:
        """
        Create an incident record
        
        Args:
            incident_data: Incident information
            
        Returns:
            Created incident
        """
        try:
            incident = {
                'id': incident_data.get('id') or f"incident-{datetime.utcnow().timestamp()}",
                'title': incident_data.get('title'),
                'description': incident_data.get('description'),
                'severity': incident_data.get('severity', IncidentSeverity.MEDIUM.value),
                'status': 'open',
                'affected_resource': incident_data.get('affected_resource'),
                'remediation_attempted': incident_data.get('remediation_attempted', False),
                'remediation_action': incident_data.get('remediation_action'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self.incident_history.append(incident)
            
            return {
                'success': True,
                'incident': incident
            }
        except Exception as e:
            logger.error(f"Failed to create incident: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def resolve_incident(self, incident_id: str, resolution: str) -> Dict:
        """
        Resolve an incident
        
        Args:
            incident_id: Incident ID
            resolution: Resolution description
            
        Returns:
            Resolution result
        """
        try:
            for incident in self.incident_history:
                if incident['id'] == incident_id:
                    incident['status'] = 'resolved'
                    incident['resolution'] = resolution
                    incident['resolved_at'] = datetime.utcnow().isoformat()
                    incident['updated_at'] = datetime.utcnow().isoformat()
                    
                    return {
                        'success': True,
                        'incident_id': incident_id,
                        'message': 'Incident resolved'
                    }
            
            return {
                'success': False,
                'error': 'Incident not found'
            }
        except Exception as e:
            logger.error(f"Failed to resolve incident: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_incident_history(self, days: int = 7, severity: Optional[str] = None) -> Dict:
        """
        Get incident history
        
        Args:
            days: Number of days to look back
            severity: Filter by severity
            
        Returns:
            Incident history
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            filtered_incidents = []
            for incident in self.incident_history:
                created_at = datetime.fromisoformat(incident['created_at'])
                
                if created_at < cutoff_date:
                    continue
                
                if severity and incident.get('severity') != severity:
                    continue
                
                filtered_incidents.append(incident)
            
            return {
                'success': True,
                'count': len(filtered_incidents),
                'incidents': filtered_incidents
            }
        except Exception as e:
            logger.error(f"Failed to get incident history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
