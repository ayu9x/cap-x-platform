import { AlertTriangle, CheckCircle, Clock, MessageSquare, User } from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';

const IncidentTimeline = ({ incidents }) => {
    const getSeverityConfig = (severity) => {
        const configs = {
            critical: {
                color: '#ef4444',
                className: 'severity-critical',
                label: 'Critical'
            },
            high: {
                color: '#f59e0b',
                className: 'severity-high',
                label: 'High'
            },
            medium: {
                color: '#3b82f6',
                className: 'severity-medium',
                label: 'Medium'
            },
            low: {
                color: '#10b981',
                className: 'severity-low',
                label: 'Low'
            }
        };
        return configs[severity] || configs.medium;
    };

    const getStatusIcon = (status) => {
        return status === 'resolved' ? CheckCircle : AlertTriangle;
    };

    return (
        <div className="incident-timeline">
            <h2 className="timeline-title">Incident Timeline</h2>

            <div className="timeline-container">
                {incidents && incidents.length > 0 ? (
                    incidents.map((incident, index) => {
                        const severityConfig = getSeverityConfig(incident.severity);
                        const StatusIcon = getStatusIcon(incident.status);

                        return (
                            <div key={incident.id} className="timeline-item">
                                <div className="timeline-marker" style={{ backgroundColor: severityConfig.color }}>
                                    <StatusIcon size={16} color="#fff" />
                                </div>

                                {index < incidents.length - 1 && <div className="timeline-line"></div>}

                                <div className="timeline-content">
                                    <div className="incident-header">
                                        <h3 className="incident-title">{incident.title}</h3>
                                        <span className={`severity-badge ${severityConfig.className}`}>
                                            {severityConfig.label}
                                        </span>
                                    </div>

                                    <p className="incident-description">{incident.description}</p>

                                    <div className="incident-meta">
                                        <div className="meta-item">
                                            <User size={14} />
                                            <span>{incident.assignedTo || 'Unassigned'}</span>
                                        </div>

                                        <div className="meta-item">
                                            <Clock size={14} />
                                            <span>{formatDistanceToNow(new Date(incident.createdAt), { addSuffix: true })}</span>
                                        </div>

                                        {incident.comments && (
                                            <div className="meta-item">
                                                <MessageSquare size={14} />
                                                <span>{incident.comments} comments</span>
                                            </div>
                                        )}
                                    </div>

                                    <div className="incident-status">
                                        <span className={`status-badge status-${incident.status}`}>
                                            {incident.status}
                                        </span>
                                        {incident.resolvedAt && (
                                            <span className="resolved-time">
                                                Resolved {format(new Date(incident.resolvedAt), 'MMM dd, yyyy HH:mm')}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <div className="timeline-empty">
                        <CheckCircle size={48} color="#10b981" />
                        <p>No incidents to display</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default IncidentTimeline;
