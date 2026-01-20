import { CheckCircle, XCircle, Clock, Circle, Play, GitBranch } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const PipelineStatus = ({ pipeline }) => {
    const {
        id,
        name,
        branch,
        status,
        stages,
        triggeredBy,
        startedAt,
        duration
    } = pipeline;

    const getStageStatusConfig = (status) => {
        const configs = {
            success: {
                icon: CheckCircle,
                className: 'stage-success',
                color: '#10b981'
            },
            failed: {
                icon: XCircle,
                className: 'stage-failed',
                color: '#ef4444'
            },
            running: {
                icon: Clock,
                className: 'stage-running',
                color: '#f59e0b'
            },
            pending: {
                icon: Circle,
                className: 'stage-pending',
                color: '#6b7280'
            }
        };
        return configs[status] || configs.pending;
    };

    const getPipelineStatusClass = (status) => {
        const classes = {
            success: 'pipeline-success',
            failed: 'pipeline-failed',
            running: 'pipeline-running',
            pending: 'pipeline-pending'
        };
        return classes[status] || 'pipeline-pending';
    };

    return (
        <div className={`pipeline-status ${getPipelineStatusClass(status)}`}>
            <div className="pipeline-header">
                <div className="pipeline-info">
                    <div className="pipeline-name-row">
                        <Play size={18} />
                        <h3 className="pipeline-name">{name}</h3>
                    </div>
                    <div className="pipeline-meta">
                        <GitBranch size={14} />
                        <span className="branch-name">{branch}</span>
                        <span className="pipeline-separator">•</span>
                        <span className="triggered-by">by {triggeredBy}</span>
                        {startedAt && (
                            <>
                                <span className="pipeline-separator">•</span>
                                <span className="started-time">
                                    {formatDistanceToNow(new Date(startedAt), { addSuffix: true })}
                                </span>
                            </>
                        )}
                    </div>
                </div>
                {duration && (
                    <div className="pipeline-duration">
                        <Clock size={14} />
                        <span>{duration}</span>
                    </div>
                )}
            </div>

            <div className="pipeline-stages">
                {stages && stages.map((stage, index) => {
                    const stageConfig = getStageStatusConfig(stage.status);
                    const StageIcon = stageConfig.icon;

                    return (
                        <div key={stage.id || index} className="pipeline-stage">
                            <div className={`stage-indicator ${stageConfig.className}`}>
                                <StageIcon size={16} color={stageConfig.color} />
                            </div>
                            <div className="stage-content">
                                <span className="stage-name">{stage.name}</span>
                                {stage.duration && (
                                    <span className="stage-duration">{stage.duration}</span>
                                )}
                            </div>
                            {index < stages.length - 1 && (
                                <div className="stage-connector"></div>
                            )}
                        </div>
                    );
                })}
            </div>

            <div className="pipeline-actions">
                <button className="btn-secondary btn-sm">View Logs</button>
                <button className="btn-primary btn-sm">Details</button>
            </div>
        </div>
    );
};

export default PipelineStatus;
