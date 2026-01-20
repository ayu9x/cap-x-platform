"""
AI Insights Service
Provides AI-powered analytics, predictions, and recommendations
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class AIInsightsService:
    """Service for AI-powered insights and recommendations"""
    
    def __init__(self):
        """Initialize AI insights service"""
        self.historical_data = defaultdict(list)
        self.predictions = []
        self.recommendations = []
    
    def analyze_deployment_patterns(self, deployments: List[Dict]) -> Dict:
        """
        Analyze deployment patterns and success rates
        
        Args:
            deployments: List of deployment records
            
        Returns:
            Deployment pattern analysis
        """
        try:
            if not deployments:
                return {
                    'success': True,
                    'message': 'No deployment data available',
                    'patterns': {}
                }
            
            # Calculate success rate
            total = len(deployments)
            successful = sum(1 for d in deployments if d.get('status') == 'success')
            failed = sum(1 for d in deployments if d.get('status') == 'failed')
            
            success_rate = (successful / total * 100) if total > 0 else 0
            
            # Analyze by time of day
            time_patterns = defaultdict(lambda: {'total': 0, 'success': 0})
            for deployment in deployments:
                created_at = deployment.get('created_at')
                if created_at:
                    hour = datetime.fromisoformat(created_at).hour
                    time_slot = f"{hour:02d}:00"
                    time_patterns[time_slot]['total'] += 1
                    if deployment.get('status') == 'success':
                        time_patterns[time_slot]['success'] += 1
            
            # Find best and worst times
            best_time = max(time_patterns.items(), 
                          key=lambda x: x[1]['success'] / x[1]['total'] if x[1]['total'] > 0 else 0)
            worst_time = min(time_patterns.items(),
                           key=lambda x: x[1]['success'] / x[1]['total'] if x[1]['total'] > 0 else 1)
            
            # Analyze by environment
            env_patterns = defaultdict(lambda: {'total': 0, 'success': 0})
            for deployment in deployments:
                env = deployment.get('environment', 'unknown')
                env_patterns[env]['total'] += 1
                if deployment.get('status') == 'success':
                    env_patterns[env]['success'] += 1
            
            return {
                'success': True,
                'total_deployments': total,
                'success_rate': round(success_rate, 2),
                'successful_deployments': successful,
                'failed_deployments': failed,
                'best_deployment_time': {
                    'time': best_time[0],
                    'success_rate': round(best_time[1]['success'] / best_time[1]['total'] * 100, 2)
                },
                'worst_deployment_time': {
                    'time': worst_time[0],
                    'success_rate': round(worst_time[1]['success'] / worst_time[1]['total'] * 100, 2)
                },
                'environment_analysis': {
                    env: {
                        'total': data['total'],
                        'success_rate': round(data['success'] / data['total'] * 100, 2)
                    }
                    for env, data in env_patterns.items()
                }
            }
        except Exception as e:
            logger.error(f"Deployment pattern analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict_resource_usage(self, historical_metrics: List[Dict], 
                              forecast_hours: int = 24) -> Dict:
        """
        Predict future resource usage based on historical data
        
        Args:
            historical_metrics: Historical metric data
            forecast_hours: Hours to forecast ahead
            
        Returns:
            Resource usage predictions
        """
        try:
            if not historical_metrics:
                return {
                    'success': True,
                    'message': 'Insufficient data for prediction',
                    'predictions': []
                }
            
            # Extract CPU and memory values
            cpu_values = [m.get('cpu', 0) for m in historical_metrics]
            memory_values = [m.get('memory', 0) for m in historical_metrics]
            
            # Simple linear trend prediction
            cpu_trend = self._calculate_trend(cpu_values)
            memory_trend = self._calculate_trend(memory_values)
            
            # Generate predictions
            predictions = []
            current_time = datetime.utcnow()
            
            for hour in range(forecast_hours):
                prediction_time = current_time + timedelta(hours=hour)
                
                predicted_cpu = cpu_values[-1] + (cpu_trend * hour)
                predicted_memory = memory_values[-1] + (memory_trend * hour)
                
                # Ensure values are within reasonable bounds
                predicted_cpu = max(0, min(100, predicted_cpu))
                predicted_memory = max(0, min(100, predicted_memory))
                
                predictions.append({
                    'timestamp': prediction_time.isoformat(),
                    'cpu_percent': round(predicted_cpu, 2),
                    'memory_percent': round(predicted_memory, 2),
                    'confidence': self._calculate_confidence(hour, len(historical_metrics))
                })
            
            return {
                'success': True,
                'forecast_hours': forecast_hours,
                'predictions': predictions,
                'trends': {
                    'cpu': 'increasing' if cpu_trend > 0 else 'decreasing',
                    'memory': 'increasing' if memory_trend > 0 else 'decreasing'
                }
            }
        except Exception as e:
            logger.error(f"Resource usage prediction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend from values"""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate slope using least squares
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        return slope
    
    def _calculate_confidence(self, hours_ahead: int, data_points: int) -> float:
        """Calculate prediction confidence based on forecast distance and data availability"""
        # Confidence decreases with forecast distance and increases with more data
        distance_factor = max(0, 1 - (hours_ahead / 48))  # Decreases over 48 hours
        data_factor = min(1, data_points / 100)  # Increases up to 100 data points
        
        confidence = (distance_factor * 0.7 + data_factor * 0.3) * 100
        return round(confidence, 2)
    
    def generate_recommendations(self, metrics: Dict, incidents: List[Dict]) -> Dict:
        """
        Generate AI-powered recommendations based on system state
        
        Args:
            metrics: Current system metrics
            incidents: Recent incidents
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            # Check CPU usage
            cpu_percent = metrics.get('cpu', {}).get('percent', 0)
            if cpu_percent > 80:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'title': 'High CPU Usage Detected',
                    'description': f'CPU usage is at {cpu_percent}%. Consider scaling up resources.',
                    'action': 'scale_up',
                    'estimated_impact': 'Improve response time by 30-40%'
                })
            
            # Check memory usage
            memory_percent = metrics.get('memory', {}).get('percent', 0)
            if memory_percent > 85:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'title': 'High Memory Usage Detected',
                    'description': f'Memory usage is at {memory_percent}%. Risk of OOM errors.',
                    'action': 'scale_up',
                    'estimated_impact': 'Prevent out-of-memory errors'
                })
            
            # Check disk usage
            disk_percent = metrics.get('disk', {}).get('percent', 0)
            if disk_percent > 90:
                recommendations.append({
                    'type': 'storage',
                    'priority': 'critical',
                    'title': 'Critical Disk Space',
                    'description': f'Disk usage is at {disk_percent}%. Immediate action required.',
                    'action': 'cleanup_or_expand',
                    'estimated_impact': 'Prevent service disruption'
                })
            
            # Analyze incident patterns
            if incidents:
                critical_incidents = [i for i in incidents if i.get('severity') == 'critical']
                if len(critical_incidents) > 3:
                    recommendations.append({
                        'type': 'reliability',
                        'priority': 'high',
                        'title': 'Frequent Critical Incidents',
                        'description': f'{len(critical_incidents)} critical incidents detected recently.',
                        'action': 'review_infrastructure',
                        'estimated_impact': 'Improve system stability'
                    })
            
            # Cost optimization
            if cpu_percent < 20 and memory_percent < 30:
                recommendations.append({
                    'type': 'cost',
                    'priority': 'medium',
                    'title': 'Resource Under-utilization',
                    'description': 'System resources are under-utilized. Consider scaling down.',
                    'action': 'scale_down',
                    'estimated_impact': 'Reduce costs by 20-30%'
                })
            
            return {
                'success': True,
                'count': len(recommendations),
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_anomalies_ml(self, metric_name: str, values: List[float], 
                           sensitivity: float = 2.0) -> Dict:
        """
        Detect anomalies using statistical methods (ML-like approach)
        
        Args:
            metric_name: Name of the metric
            values: Time series values
            sensitivity: Sensitivity threshold (standard deviations)
            
        Returns:
            Anomaly detection results
        """
        try:
            if len(values) < 10:
                return {
                    'success': True,
                    'message': 'Insufficient data for anomaly detection',
                    'anomalies': []
                }
            
            # Calculate statistics
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            
            # Detect anomalies
            anomalies = []
            for i, value in enumerate(values):
                z_score = abs((value - mean) / stdev) if stdev > 0 else 0
                
                if z_score > sensitivity:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'z_score': round(z_score, 2),
                        'deviation_percent': round(((value - mean) / mean * 100), 2),
                        'severity': 'high' if z_score > 3 else 'medium'
                    })
            
            return {
                'success': True,
                'metric': metric_name,
                'total_points': len(values),
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies,
                'statistics': {
                    'mean': round(mean, 2),
                    'std_dev': round(stdev, 2),
                    'min': round(min(values), 2),
                    'max': round(max(values), 2)
                }
            }
        except Exception as e:
            logger.error(f"ML anomaly detection failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_incident_root_cause(self, incident: Dict, related_metrics: Dict) -> Dict:
        """
        Analyze potential root causes of an incident
        
        Args:
            incident: Incident data
            related_metrics: Metrics around the time of incident
            
        Returns:
            Root cause analysis
        """
        try:
            potential_causes = []
            
            # Check for resource exhaustion
            if related_metrics.get('cpu', {}).get('percent', 0) > 90:
                potential_causes.append({
                    'cause': 'CPU Exhaustion',
                    'confidence': 0.85,
                    'evidence': f"CPU usage was at {related_metrics['cpu']['percent']}%",
                    'recommendation': 'Scale up CPU resources or optimize application code'
                })
            
            if related_metrics.get('memory', {}).get('percent', 0) > 90:
                potential_causes.append({
                    'cause': 'Memory Exhaustion',
                    'confidence': 0.90,
                    'evidence': f"Memory usage was at {related_metrics['memory']['percent']}%",
                    'recommendation': 'Increase memory allocation or fix memory leaks'
                })
            
            # Check for network issues
            if related_metrics.get('network', {}).get('errors', 0) > 100:
                potential_causes.append({
                    'cause': 'Network Issues',
                    'confidence': 0.75,
                    'evidence': f"Network errors detected: {related_metrics['network']['errors']}",
                    'recommendation': 'Check network configuration and connectivity'
                })
            
            # If no specific cause found
            if not potential_causes:
                potential_causes.append({
                    'cause': 'Unknown',
                    'confidence': 0.30,
                    'evidence': 'No clear resource exhaustion detected',
                    'recommendation': 'Review application logs and recent changes'
                })
            
            # Sort by confidence
            potential_causes.sort(key=lambda x: x['confidence'], reverse=True)
            
            return {
                'success': True,
                'incident_id': incident.get('id'),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'most_likely_cause': potential_causes[0] if potential_causes else None,
                'all_potential_causes': potential_causes
            }
        except Exception as e:
            logger.error(f"Root cause analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_health_score(self, metrics: Dict, incidents: List[Dict]) -> Dict:
        """
        Calculate overall system health score
        
        Args:
            metrics: Current system metrics
            incidents: Recent incidents
            
        Returns:
            Health score and breakdown
        """
        try:
            scores = {}
            
            # Performance score (40% weight)
            cpu_score = max(0, 100 - metrics.get('cpu', {}).get('percent', 0))
            memory_score = max(0, 100 - metrics.get('memory', {}).get('percent', 0))
            disk_score = max(0, 100 - metrics.get('disk', {}).get('percent', 0))
            performance_score = (cpu_score + memory_score + disk_score) / 3
            scores['performance'] = round(performance_score, 2)
            
            # Reliability score (40% weight)
            open_incidents = len([i for i in incidents if i.get('status') != 'resolved'])
            critical_incidents = len([i for i in incidents if i.get('severity') == 'critical'])
            reliability_score = max(0, 100 - (open_incidents * 10) - (critical_incidents * 20))
            scores['reliability'] = round(reliability_score, 2)
            
            # Availability score (20% weight)
            # Simplified - would normally check uptime
            availability_score = 95.0  # Placeholder
            scores['availability'] = availability_score
            
            # Calculate overall score
            overall_score = (
                performance_score * 0.4 +
                reliability_score * 0.4 +
                availability_score * 0.2
            )
            
            # Determine health status
            if overall_score >= 90:
                status = 'excellent'
            elif overall_score >= 75:
                status = 'good'
            elif overall_score >= 60:
                status = 'fair'
            elif overall_score >= 40:
                status = 'poor'
            else:
                status = 'critical'
            
            return {
                'success': True,
                'overall_score': round(overall_score, 2),
                'status': status,
                'breakdown': scores,
                'calculated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health score calculation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }