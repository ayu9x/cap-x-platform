import { useState, useEffect } from 'react';
import { Plus, Search, Filter, GitBranch, Play } from 'lucide-react';
import { pipelinesAPI } from '../services/api';
import PipelineStatus from '../components/PipelineStatus';
import AlertBanner from '../components/AlertBanner';

const Pipelines = () => {
    const [pipelines, setPipelines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [showCreateModal, setShowCreateModal] = useState(false);

    useEffect(() => {
        fetchPipelines();
    }, []);

    const fetchPipelines = async () => {
        try {
            setLoading(true);
            const response = await pipelinesAPI.getAll();
            setPipelines(response.data || []);
            setError(null);
        } catch (err) {
            setError('Failed to load pipelines. Please try again.');
            console.error('Error fetching pipelines:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleTrigger = async (pipelineId) => {
        try {
            await pipelinesAPI.trigger(pipelineId);
            alert('Pipeline triggered successfully!');
            fetchPipelines();
        } catch (err) {
            alert('Failed to trigger pipeline');
            console.error('Error triggering pipeline:', err);
        }
    };

    const handleCancel = async (pipelineId) => {
        try {
            await pipelinesAPI.cancel(pipelineId);
            alert('Pipeline cancelled');
            fetchPipelines();
        } catch (err) {
            alert('Failed to cancel pipeline');
            console.error('Error cancelling pipeline:', err);
        }
    };

    const filteredPipelines = pipelines.filter((pipeline) => {
        const matchesSearch = pipeline.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            pipeline.branch?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesFilter = filterStatus === 'all' || pipeline.status === filterStatus;
        return matchesSearch && matchesFilter;
    });

    const pipelineStats = {
        total: pipelines.length,
        running: pipelines.filter(p => p.status === 'running').length,
        success: pipelines.filter(p => p.status === 'success').length,
        failed: pipelines.filter(p => p.status === 'failed').length,
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">CI/CD Pipelines</h1>
                    <p className="page-subtitle">Manage and monitor your deployment pipelines</p>
                </div>
                <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                    <Plus size={20} />
                    New Pipeline
                </button>
            </div>

            {error && (
                <AlertBanner
                    type="error"
                    message={error}
                    dismissible={true}
                    onDismiss={() => setError(null)}
                />
            )}

            <div className="stats-bar">
                <div className="stat-box">
                    <span className="stat-value">{pipelineStats.total}</span>
                    <span className="stat-label">Total Pipelines</span>
                </div>
                <div className="stat-box stat-running">
                    <span className="stat-value">{pipelineStats.running}</span>
                    <span className="stat-label">Running</span>
                </div>
                <div className="stat-box stat-success">
                    <span className="stat-value">{pipelineStats.success}</span>
                    <span className="stat-label">Successful</span>
                </div>
                <div className="stat-box stat-failed">
                    <span className="stat-value">{pipelineStats.failed}</span>
                    <span className="stat-label">Failed</span>
                </div>
            </div>

            <div className="page-filters">
                <div className="search-box">
                    <Search size={20} />
                    <input
                        type="text"
                        placeholder="Search pipelines..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="search-input"
                    />
                </div>

                <div className="filter-group">
                    <Filter size={20} />
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Status</option>
                        <option value="running">Running</option>
                        <option value="success">Success</option>
                        <option value="failed">Failed</option>
                        <option value="pending">Pending</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading pipelines...</p>
                </div>
            ) : (
                <div className="pipelines-list">
                    {filteredPipelines.length > 0 ? (
                        filteredPipelines.map((pipeline) => (
                            <PipelineStatus key={pipeline.id} pipeline={pipeline} />
                        ))
                    ) : (
                        <div className="empty-state">
                            <GitBranch size={64} color="#9ca3af" />
                            <h3>No pipelines found</h3>
                            <p>
                                {searchQuery || filterStatus !== 'all'
                                    ? 'Try adjusting your filters'
                                    : 'Create your first pipeline to get started'}
                            </p>
                            <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                                <Plus size={20} />
                                Create Pipeline
                            </button>
                        </div>
                    )}
                </div>
            )}

            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Create New Pipeline</h2>
                        <p>Pipeline configuration form would go here</p>
                        <button className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Pipelines;