import { useState, useEffect } from 'react';
import { Plus, Search, Filter, AlertTriangle } from 'lucide-react';
import { incidentsAPI } from '../services/api';
import IncidentTimeline from '../components/IncidentTimeline';
import AlertBanner from '../components/AlertBanner';

const Incidents = () => {
    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterSeverity, setFilterSeverity] = useState('all');
    const [filterStatus, setFilterStatus] = useState('all');
    const [showCreateModal, setShowCreateModal] = useState(false);

    useEffect(() => {
        fetchIncidents();
    }, []);

    const fetchIncidents = async () => {
        try {
            setLoading(true);
            const response = await incidentsAPI.getAll();
            setIncidents(response.data || []);
            setError(null);
        } catch (err) {
            setError('Failed to load incidents. Please try again.');
            console.error('Error fetching incidents:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleResolve = async (incidentId) => {
        try {
            await incidentsAPI.resolve(incidentId, { resolution: 'Resolved manually' });
            fetchIncidents();
        } catch (err) {
            alert('Failed to resolve incident');
            console.error('Error resolving incident:', err);
        }
    };

    const filteredIncidents = incidents.filter((incident) => {
        const matchesSearch = incident.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            incident.description?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesSeverity = filterSeverity === 'all' || incident.severity === filterSeverity;
        const matchesStatus = filterStatus === 'all' || incident.status === filterStatus;
        return matchesSearch && matchesSeverity && matchesStatus;
    });

    const incidentStats = {
        total: incidents.length,
        critical: incidents.filter(i => i.severity === 'critical').length,
        high: incidents.filter(i => i.severity === 'high').length,
        open: incidents.filter(i => i.status !== 'resolved').length,
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Incidents</h1>
                    <p className="page-subtitle">Track and manage platform incidents</p>
                </div>
                <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                    <Plus size={20} />
                    Report Incident
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
                    <span className="stat-value">{incidentStats.total}</span>
                    <span className="stat-label">Total Incidents</span>
                </div>
                <div className="stat-box stat-critical">
                    <span className="stat-value">{incidentStats.critical}</span>
                    <span className="stat-label">Critical</span>
                </div>
                <div className="stat-box stat-high">
                    <span className="stat-value">{incidentStats.high}</span>
                    <span className="stat-label">High Priority</span>
                </div>
                <div className="stat-box stat-open">
                    <span className="stat-value">{incidentStats.open}</span>
                    <span className="stat-label">Open</span>
                </div>
            </div>

            <div className="page-filters">
                <div className="search-box">
                    <Search size={20} />
                    <input
                        type="text"
                        placeholder="Search incidents..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="search-input"
                    />
                </div>

                <div className="filter-group">
                    <Filter size={20} />
                    <select
                        value={filterSeverity}
                        onChange={(e) => setFilterSeverity(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Severities</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>

                <div className="filter-group">
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Status</option>
                        <option value="open">Open</option>
                        <option value="investigating">Investigating</option>
                        <option value="resolved">Resolved</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading incidents...</p>
                </div>
            ) : (
                <div className="incidents-container">
                    {filteredIncidents.length > 0 ? (
                        <IncidentTimeline incidents={filteredIncidents} />
                    ) : (
                        <div className="empty-state">
                            <AlertTriangle size={64} color="#9ca3af" />
                            <h3>No incidents found</h3>
                            <p>
                                {searchQuery || filterSeverity !== 'all' || filterStatus !== 'all'
                                    ? 'Try adjusting your filters'
                                    : 'All systems are running smoothly'}
                            </p>
                        </div>
                    )}
                </div>
            )}

            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Report New Incident</h2>
                        <p>Incident reporting form would go here</p>
                        <button className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Incidents;