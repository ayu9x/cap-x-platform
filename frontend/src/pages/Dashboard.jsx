import { useState, useEffect } from 'react';
import { Rocket, AlertTriangle, Activity, Package, TrendingUp, GitBranch } from 'lucide-react';
import { dashboardAPI } from '../services/api';
import MetricCard from '../components/MetricCard';
import DeploymentCard from '../components/DeploymentCard';
import AlertBanner from '../components/AlertBanner';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [recentDeployments, setRecentDeployments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const [statsRes, activityRes] = await Promise.all([
                dashboardAPI.getStats(),
                dashboardAPI.getRecentActivity({ limit: 5 })
            ]);

            setStats(statsRes.data || {});
            setRecentDeployments(activityRes.data?.deployments || []);
            setError(null);
        } catch (err) {
            setError('Failed to load dashboard data');
            console.error('Error fetching dashboard:', err);
        } finally {
            setLoading(false);
        }
    };

    // Mock data for the chart
    const performanceData = [
        { time: '00:00', value: 65 },
        { time: '04:00', value: 72 },
        { time: '08:00', value: 85 },
        { time: '12:00', value: 78 },
        { time: '16:00', value: 90 },
        { time: '20:00', value: 82 },
        { time: '24:00', value: 88 },
    ];

    if (loading) {
        return (
            <div className="page-container">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Dashboard</h1>
                    <p className="page-subtitle">Overview of your cloud platform</p>
                </div>
            </div>

            {error && (
                <AlertBanner
                    type="error"
                    message={error}
                    dismissible={true}
                    onDismiss={() => setError(null)}
                />
            )}

            <div className="metrics-grid">
                <MetricCard
                    title="Total Applications"
                    value={stats?.totalApplications || 12}
                    trend="up"
                    trendValue="+3"
                    icon={Package}
                    color="#3b82f6"
                />
                <MetricCard
                    title="Active Deployments"
                    value={stats?.activeDeployments || 24}
                    trend="up"
                    trendValue="+12%"
                    icon={Rocket}
                    color="#10b981"
                />
                <MetricCard
                    title="Open Incidents"
                    value={stats?.openIncidents || 3}
                    trend="down"
                    trendValue="-2"
                    icon={AlertTriangle}
                    color="#ef4444"
                />
                <MetricCard
                    title="System Uptime"
                    value={stats?.systemUptime || "99.9"}
                    unit="%"
                    trend="up"
                    trendValue="+0.1%"
                    icon={Activity}
                    color="#8b5cf6"
                />
            </div>

            <div className="dashboard-content">
                <div className="dashboard-section">
                    <div className="section-header">
                        <h2 className="section-title">Performance Metrics</h2>
                        <select className="time-range-select">
                            <option>Last 24 hours</option>
                            <option>Last 7 days</option>
                            <option>Last 30 days</option>
                        </select>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={performanceData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis dataKey="time" stroke="#6b7280" />
                                <YAxis stroke="#6b7280" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#fff',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    dot={{ fill: '#3b82f6', r: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="dashboard-section">
                    <div className="section-header">
                        <h2 className="section-title">Recent Deployments</h2>
                        <a href="/deployments" className="section-link">View All</a>
                    </div>
                    <div className="deployments-list">
                        {recentDeployments.length > 0 ? (
                            recentDeployments.map((deployment) => (
                                <DeploymentCard key={deployment.id} deployment={deployment} />
                            ))
                        ) : (
                            <div className="empty-state-small">
                                <Rocket size={48} color="#9ca3af" />
                                <p>No recent deployments</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="dashboard-section">
                    <div className="section-header">
                        <h2 className="section-title">Quick Actions</h2>
                    </div>
                    <div className="quick-actions-grid">
                        <button className="quick-action-card">
                            <Rocket size={24} />
                            <span>New Deployment</span>
                        </button>
                        <button className="quick-action-card">
                            <Package size={24} />
                            <span>Create Application</span>
                        </button>
                        <button className="quick-action-card">
                            <GitBranch size={24} />
                            <span>Run Pipeline</span>
                        </button>
                        <button className="quick-action-card">
                            <Activity size={24} />
                            <span>View Monitoring</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;