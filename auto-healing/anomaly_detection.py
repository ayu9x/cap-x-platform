"""
Anomaly Detection Service
Uses statistical methods to detect unusual patterns
"""
import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import statistics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/capx_platform')
        self.client = MongoClient(mongo_uri)
        self.db = self.client.capx_platform
    
    def detect_metric_anomalies(self, application_id, metric_type='cpu', hours=24):
        """Detect anomalies in application metrics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get metrics from database
        metrics = list(self.db.metrics.find({
            'application_id': application_id,
            'metric_type': metric_type,
            'timestamp': {'$gte': cutoff_time}
        }).sort('timestamp', 1))
        
        if len(metrics) < 20:
            logger.info(f"Insufficient data for anomaly detection (need 20+, have {len(metrics)})")
            return {'anomalies': [], 'status': 'insufficient_data'}
        
        values = [m['value'] for m in metrics]
        
        # Calculate baseline statistics (exclude recent data)
        baseline_values = values[:-10]  # Use all but last 10 points as baseline
        mean = statistics.mean(baseline_values)
        stdev = statistics.stdev(baseline_values)
        
        # Detect anomalies in recent data (Z-score method)
        anomalies = []
        threshold = 3  # 3 standard deviations
        
        for i, metric in enumerate(metrics[-10:]):
            z_score = (metric['value'] - mean) / stdev if stdev > 0 else 0
            
            if abs(z_score) > threshold:
                anomalies.append({
                    'timestamp': metric['timestamp'],
                    'value': metric['value'],
                    'z_score': round(z_score, 2),
                    'deviation': round(abs(metric['value'] - mean), 2),
                    'severity': 'high' if abs(z_score) > 4 else 'medium'
                })
                
                logger.warning(f"Anomaly detected: {metric_type}={metric['value']}, z-score={z_score:.2f}")
        
        return {
            'anomalies': anomalies,
            'status': 'completed',
            'baseline': {
                'mean': round(mean, 2),
                'stdev': round(stdev, 2),
                'data_points': len(baseline_values)
            },
            'threshold': threshold
        }
    
    def detect_deployment_anomalies(self, application_id, days=30):
        """Detect unusual deployment patterns"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get deployment history
        deployments = list(self.db.deployments.find({
            'application_id': application_id,
            'created_at': {'$gte': cutoff_date}
        }).sort('created_at', 1))
        
        if len(deployments) < 5:
            return {'anomalies': [], 'status': 'insufficient_data'}
        
        anomalies = []
        
        # Check for deployment failures
        recent_deployments = deployments[-10:]
        failed_count = sum(1 for d in recent_deployments if d['status'] == 'failed')
        
        if failed_count > 3:
            anomalies.append({
                'type': 'high_failure_rate',
                'description': f'High deployment failure rate: {failed_count}/10 recent deployments failed',
                'severity': 'high',
                'recommendation': 'Review deployment process and application logs'
            })
        
        # Check for unusual deployment frequency
        if len(deployments) > 50:
            avg_time_between = (deployments[-1]['created_at'] - deployments[0]['created_at']).total_seconds() / len(deployments)
            
            # Check recent deployment frequency
            recent_time_between = (deployments[-1]['created_at'] - deployments[-5]['created_at']).total_seconds() / 5
            
            if recent_time_between < avg_time_between * 0.5:
                anomalies.append({
                    'type': 'increased_deployment_frequency',
                    'description': 'Deployment frequency has increased significantly',
                    'severity': 'medium',
                    'recommendation': 'May indicate instability or hotfix cycle'
                })
        
        # Check for rollbacks
        rollback_count = sum(1 for d in recent_deployments if d['status'] == 'rolled_back')
        
        if rollback_count > 2:
            anomalies.append({
                'type': 'frequent_rollbacks',
                'description': f'{rollback_count} rollbacks in recent deployments',
                'severity': 'high',
                'recommendation': 'Improve testing and deployment validation'
            })
        
        return {
            'anomalies': anomalies,
            'status': 'completed',
            'deployment_stats': {
                'total': len(deployments),
                'failed': failed_count,
                'rolled_back': rollback_count
            }
        }
    
    def detect_incident_patterns(self, application_id, days=30):
        """Detect patterns in incidents"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        incidents = list(self.db.incidents.find({
            'application_id': application_id,
            'created_at': {'$gte': cutoff_date}
        }).sort('created_at', 1))
        
        if len(incidents) < 3:
            return {'patterns': [], 'status': 'insufficient_data'}
        
        patterns = []
        
        # Group by incident type
        incident_types = {}
        for incident in incidents:
            itype = incident.get('incident_type', 'unknown')
            incident_types[itype] = incident_types.get(itype, 0) + 1
        
        # Find recurring issues
        for itype, count in incident_types.items():
            if count > 5:
                patterns.append({
                    'type': 'recurring_incident',
                    'incident_type': itype,
                    'occurrences': count,
                    'severity': 'high',
                    'recommendation': f'Implement permanent fix for {itype}'
                })
        
        # Check for increasing incident rate
        if len(incidents) > 10:
            recent_incidents = [i for i in incidents if i['created_at'] > datetime.utcnow() - timedelta(days=7)]
            older_incidents = [i for i in incidents if i['created_at'] <= datetime.utcnow() - timedelta(days=7)]
            
            recent_rate = len(recent_incidents) / 7
            older_rate = len(older_incidents) / (days - 7)
            
            if recent_rate > older_rate * 1.5:
                patterns.append({
                    'type': 'increasing_incident_rate',
                    'description': 'Incident rate has increased recently',
                    'severity': 'high',
                    'recent_rate': round(recent_rate, 2),
                    'baseline_rate': round(older_rate, 2),
                    'recommendation': 'Investigate recent changes or deployments'
                })
        
        # Check MTTR trends
        resolved_incidents = [i for i in incidents if i.get('mttr')]
        if len(resolved_incidents) > 5:
            mttrs = [i['mttr'] for i in resolved_incidents]
            avg_mttr = statistics.mean(mttrs)
            recent_mttr = statistics.mean(mttrs[-5:])
            
            if recent_mttr > avg_mttr * 1.3:
                patterns.append({
                    'type': 'increasing_mttr',
                    'description': 'Mean time to resolve has increased',
                    'severity': 'medium',
                    'avg_mttr_minutes': round(avg_mttr / 60, 2),
                    'recent_mttr_minutes': round(recent_mttr / 60, 2),
                    'recommendation': 'Review incident response procedures'
                })
        
        return {
            'patterns': patterns,
            'status': 'completed',
            'incident_stats': {
                'total': len(incidents),
                'by_type': incident_types
            }
        }
    
    def run_comprehensive_analysis(self, application_id):
        """Run all anomaly detection checks"""
        logger.info(f"Running comprehensive anomaly analysis for {application_id}")
        
        results = {
            'application_id': application_id,
            'timestamp': datetime.utcnow().isoformat(),
            'analyses': {}
        }
        
        # Metric anomalies
        for metric_type in ['cpu', 'memory', 'latency', 'errors']:
            results['analyses'][f'{metric_type}_anomalies'] = self.detect_metric_anomalies(
                application_id, metric_type
            )
        
        # Deployment anomalies
        results['analyses']['deployment_anomalies'] = self.detect_deployment_anomalies(application_id)
        
        # Incident patterns
        results['analyses']['incident_patterns'] = self.detect_incident_patterns(application_id)
        
        # Aggregate findings
        all_anomalies = []
        for analysis in results['analyses'].values():
            if 'anomalies' in analysis:
                all_anomalies.extend(analysis['anomalies'])
            if 'patterns' in analysis:
                all_anomalies.extend(analysis['patterns'])
        
        results['summary'] = {
            'total_anomalies': len(all_anomalies),
            'high_severity': sum(1 for a in all_anomalies if a.get('severity') == 'high'),
            'medium_severity': sum(1 for a in all_anomalies if a.get('severity') == 'medium'),
            'overall_health': 'critical' if any(a.get('severity') == 'high' for a in all_anomalies) else 'healthy'
        }
        
        return results


if __name__ == '__main__':
    import time
    
    logger.info("Starting Anomaly Detection Service...")
    
    detector = AnomalyDetector()
    
    while True:
        try:
            # Get all active applications
            applications = list(detector.db.applications.find({'status': 'active'}))
            
            for app in applications:
                app_id = str(app['_id'])
                logger.info(f"Analyzing {app['name']}...")
                
                results = detector.run_comprehensive_analysis(app_id)
                
                if results['summary']['total_anomalies'] > 0:
                    logger.warning(f"Found {results['summary']['total_anomalies']} anomalies for {app['name']}")
                
            # Sleep for 5 minutes
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            time.sleep(60)