import { useState, useEffect } from 'react';
import { Plus, Search, Filter, Package, Rocket, Activity } from 'lucide-react';
import { applicationsAPI, deploymentsAPI } from '../services/api';
import AlertBanner from '../components/AlertBanner';

const Applications = () => {
    const [applications, setApplications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [showCreateModal, setShowCreateModal] = useState(false);

    useEffect(() => {
        fetchApplications();
    }, []);

    const fetchApplications = async () => {
        try {
            setLoading(true);
            const response = await applicationsAPI.getAll();
            setApplications(response.data || []);
            setError(null);
        } catch (err) {
            setError('Failed to load applications. Please try again.');
            console.error('Error fetching applications:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDeploy = async (appId) => {
        try {
            await deploymentsAPI.create({ applicationId: appId });
            alert('Deployment initiated successfully!');
            fetchApplications();
        } catch (err) {
            alert('Failed to initiate deployment');
            console.error('Error deploying application:', err);
        }
    };

    const filteredApplications = applications.filter((app) => {
        const matchesSearch = app.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            app.description?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesFilter = filterStatus === 'all' || app.status === filterStatus;
        return matchesSearch && matchesFilter;
    });

    const getStatusClass = (status) => {
        const classes = {
            active: 'status-active',
            inactive: 'status-inactive',
            deploying: 'status-deploying',
            error: 'status-error'
        };
        return classes[status] || 'status-inactive';
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Applications</h1>
                    <p className="page-subtitle">Manage and monitor your cloud applications</p>
                </div>
                <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                    <Plus size={20} />
                    New Application
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

            <div className="page-filters">
                <div className="search-box">
                    <Search size={20} />
                    <input
                        type="text"
                        placeholder="Search applications..."
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
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="deploying">Deploying</option>
                        <option value="error">Error</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading applications...</p>
                </div>
            ) : (
                <div className="applications-grid">
                    {filteredApplications.length > 0 ? (
                        filteredApplications.map((app) => (
                            <div key={app.id} className="application-card">
                                <div className="app-card-header">
                                    <div className="app-icon">
                                        <Package size={24} />
                                    </div>
                                    <span className={`app-status ${getStatusClass(app.status)}`}>
                                        {app.status || 'inactive'}
                                    </span>
                                </div>

                                <div className="app-card-body">
                                    <h3 className="app-name">{app.name}</h3>
                                    <p className="app-description">{app.description || 'No description available'}</p>

                                    <div className="app-stats">
                                        <div className="stat-item">
                                            <Rocket size={16} />
                                            <span>{app.deploymentCount || 0} deployments</span>
                                        </div>
                                        <div className="stat-item">
                                            <Activity size={16} />
                                            <span>{app.uptime || '99.9'}% uptime</span>
                                        </div>
                                    </div>

                                    <div className="app-meta">
                                        <span className="meta-label">Version:</span>
                                        <span className="meta-value">{app.version || 'N/A'}</span>
                                    </div>

                                    <div className="app-meta">
                                        <span className="meta-label">Environment:</span>
                                        <span className={`env-badge env-${app.environment}`}>
                                            {app.environment || 'development'}
                                        </span>
                                    </div>
                                </div>

                                <div className="app-card-footer">
                                    <button className="btn-secondary btn-sm">View Details</button>
                                    <button
                                        className="btn-primary btn-sm"
                                        onClick={() => handleDeploy(app.id)}
                                    >
                                        Deploy
                                    </button>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="empty-state">
                            <Package size={64} color="#9ca3af" />
                            <h3>No applications found</h3>
                            <p>Create your first application to get started</p>
                            <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                                <Plus size={20} />
                                Create Application
                            </button>
                        </div>
                    )}
                </div>
            )}

            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Create New Application</h2>
                        <p>Application creation form would go here</p>
                        <button className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Applications;
