"""
Incident Model for CAP-X Platform
Tracks auto-healing incidents and resolutions
"""

from datetime import datetime
from bson import ObjectId


class Incident:
    """Incident model for auto-healing system"""
    
    STATUSES = ['open', 'investigating', 'resolved', 'closed']
    SEVERITIES = ['low', 'medium', 'high', 'critical']
    TYPES = [
        'pod_crash_loop', 'high_memory', 'high_cpu', 'pod_not_ready',
        'service_unavailable', 'deployment_failed', 'health_check_failed', 'other'
    ]
    
    @staticmethod
    def create(db, application_id, application_name, incident_type, severity, description, **kwargs):
        """Create a new incident"""
        incident_data = {
            'application_id': ObjectId(application_id) if isinstance(application_id, str) else application_id,
            'application_name': application_name,
            'type': incident_type,
            'severity': severity,
            'status': 'open',
            'description': description,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'detected_at': datetime.utcnow(),
            'resolved_at': None,
            'closed_at': None,
            'environment': kwargs.get('environment', 'production'),
            'affected_resources': kwargs.get('affected_resources', []),
            'timeline': [
                {
                    'timestamp': datetime.utcnow(),
                    'event': 'Incident detected',
                    'details': description
                }
            ],
            'remediation': {
                'auto_remediation_attempted': False,
                'auto_remediation_successful': False,
                'remediation_actions': [],
                'manual_intervention_required': False
            },
            'metrics': {
                'mttr_minutes': 0,  # Mean Time To Resolve
                'detection_to_resolution': 0,
                'impact_duration': 0
            },
            'metadata': kwargs.get('metadata', {}),
            'assigned_to': kwargs.get('assigned_to', None),
            'tags': kwargs.get('tags', [])
        }
        
        result = db.incidents.insert_one(incident_data)
        incident_data['_id'] = result.inserted_id
        return incident_data
    
    @staticmethod
    def get_by_id(db, incident_id):
        """Get incident by ID"""
        if isinstance(incident_id, str):
            incident_id = ObjectId(incident_id)
        return db.incidents.find_one({'_id': incident_id})
    
    @staticmethod
    def update_status(db, incident_id, status, details=None):
        """Update incident status"""
        if isinstance(incident_id, str):
            incident_id = ObjectId(incident_id)
        
        if status not in Incident.STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {Incident.STATUSES}")
        
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        # Add timeline event
        timeline_event = {
            'timestamp': datetime.utcnow(),
            'event': f'Status changed to {status}',
            'details': details or f'Incident status updated to {status}'
        }
        
        if status == 'resolved':
            update_data['resolved_at'] = datetime.utcnow()
            
            # Calculate MTTR
            incident = db.incidents.find_one({'_id': incident_id})
            if incident:
                mttr = (update_data['resolved_at'] - incident['detected_at']).total_seconds() / 60
                update_data['metrics.mttr_minutes'] = round(mttr, 2)
        
        if status == 'closed':
            update_data['closed_at'] = datetime.utcnow()
        
        result = db.incidents.update_one(
            {'_id': incident_id},
            {
                '$set': update_data,
                '$push': {'timeline': timeline_event}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_timeline_event(db, incident_id, event, details):
        """Add an event to incident timeline"""
        if isinstance(incident_id, str):
            incident_id = ObjectId(incident_id)
        
        timeline_event = {
            'timestamp': datetime.utcnow(),
            'event': event,
            'details': details
        }
        
        result = db.incidents.update_one(
            {'_id': incident_id},
            {
                '$push': {'timeline': timeline_event},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_remediation_action(db, incident_id, action, success=False):
        """Add a remediation action to incident"""
        if isinstance(incident_id, str):
            incident_id = ObjectId(incident_id)
        
        remediation_action = {
            'timestamp': datetime.utcnow(),
            'action': action,
            'success': success
        }
        
        update_data = {
            'remediation.auto_remediation_attempted': True,
            'updated_at': datetime.utcnow()
        }
        
        if success:
            update_data['remediation.auto_remediation_successful'] = True
        
        result = db.incidents.update_one(
            {'_id': incident_id},
            {
                '$push': {'remediation.remediation_actions': remediation_action},
                '$set': update_data
            }
        )
        
        # Add to timeline
        Incident.add_timeline_event(
            db, incident_id,
            'Remediation action attempted',
            f"{action} - {'Success' if success else 'Failed'}"
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def list_by_application(db, application_id, skip=0, limit=20):
        """List incidents for a specific application"""
        if isinstance(application_id, str):
            application_id = ObjectId(application_id)
        
        incidents = list(
            db.incidents.find({'application_id': application_id})
            .skip(skip)
            .limit(limit)
            .sort('created_at', -1)
        )
        total = db.incidents.count_documents({'application_id': application_id})
        
        return {
            'incidents': incidents,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def list_all(db, skip=0, limit=50, status=None, severity=None):
        """List all incidents with pagination and filters"""
        query = {}
        if status:
            query['status'] = status
        if severity:
            query['severity'] = severity
        
        incidents = list(
            db.incidents.find(query)
            .skip(skip)
            .limit(limit)
            .sort('created_at', -1)
        )
        total = db.incidents.count_documents(query)
        
        return {
            'incidents': incidents,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    @staticmethod
    def get_open_incidents(db):
        """Get all open incidents"""
        return list(
            db.incidents.find({'status': {'$in': ['open', 'investigating']}})
            .sort('severity', -1)
            .sort('created_at', -1)
        )
    
    @staticmethod
    def get_stats(db, application_id=None):
        """Get incident statistics"""
        query = {}
        if application_id:
            if isinstance(application_id, str):
                application_id = ObjectId(application_id)
            query['application_id'] = application_id
        
        total = db.incidents.count_documents(query)
        open_count = db.incidents.count_documents({**query, 'status': 'open'})
        resolved = db.incidents.count_documents({**query, 'status': 'resolved'})
        critical = db.incidents.count_documents({**query, 'severity': 'critical'})
        
        # Calculate average MTTR
        pipeline = [
            {'$match': {**query, 'status': 'resolved', 'metrics.mttr_minutes': {'$gt': 0}}},
            {'$group': {
                '_id': None,
                'avg_mttr': {'$avg': '$metrics.mttr_minutes'}
            }}
        ]
        avg_result = list(db.incidents.aggregate(pipeline))
        avg_mttr = avg_result[0]['avg_mttr'] if avg_result else 0
        
        # Auto-remediation success rate
        auto_remediated = db.incidents.count_documents({
            **query,
            'remediation.auto_remediation_successful': True
        })
        auto_remediation_rate = (auto_remediated / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'open': open_count,
            'resolved': resolved,
            'critical': critical,
            'avg_mttr_minutes': round(avg_mttr, 2),
            'auto_remediation_success_rate': round(auto_remediation_rate, 2)
        }