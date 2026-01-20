import { Calendar, User, GitBranch, CheckCircle, XCircle, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const DeploymentCard = ({ deployment }) => {
    const {
        id,
        applicationName,
        version,
        environment,
        status,
        deployedBy,
        deployedAt,
        branch,
        commitHash
    } = deployment;

    const getStatusConfig = (status) => {
        const configs = {
            success: {
                icon: CheckCircle,
                className: 'status-success',
                label: 'Deployed',
                color: '#10b981'
            },
            failed: {
                icon: XCircle,
                className: 'status-failed',
                label: 'Failed',
                color: '#ef4444'
            },
            in_progress: {
                icon: Clock,
                className: 'status-progress',
                label: 'In Progress',
                color: '#f59e0b'
            }
        };
        return configs[status] || configs.in_progress;
    };

    const statusConfig = getStatusConfig(status);
    const StatusIcon = statusConfig.icon;

    return (
        <div className="deployment-card">
            <div className="deployment-header">
                <div className="deployment-info">
                    <h3 className="deployment-title">{applicationName}</h3>
                    <span className="deployment-version">v{version}</span>
                </div>
                <div className={`deployment-status ${statusConfig.className}`}>
                    <StatusIcon size={16} color={statusConfig.color} />
                    <span>{statusConfig.label}</span>
                </div>
            </div>

            <div className="deployment-body">
                <div className="deployment-detail">
                    <span className="detail-label">Environment:</span>
                    <span className={`environment-badge env-${environment}`}>
                        {environment}
                    </span>
                </div>

                <div className="deployment-detail">
                    <GitBranch size={16} />
                    <span className="detail-text">{branch}</span>
                    <span className="commit-hash">{commitHash?.substring(0, 7)}</span>
                </div>

                <div className="deployment-detail">
                    <User size={16} />
                    <span className="detail-text">{deployedBy}</span>
                </div>

                <div className="deployment-detail">
                    <Calendar size={16} />
                    <span className="detail-text">
                        {formatDistanceToNow(new Date(deployedAt), { addSuffix: true })}
                    </span>
                </div>
            </div>

            <div className="deployment-footer">
                <button className="btn-secondary btn-sm">View Logs</button>
                <button className="btn-primary btn-sm">Details</button>
            </div>
        </div>
    );
};

export default DeploymentCard;
