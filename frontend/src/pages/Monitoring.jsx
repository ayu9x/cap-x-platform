import { useState, useEffect } from 'react';
import { Activity, Cpu, HardDrive, Zap, RefreshCw } from 'lucide-react';
import { monitoringAPI } from '../services/api';
import MetricCard from '../components/MetricCard';
import AlertBanner from '../components/AlertBanner';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const Monitoring = () => {
    const [metrics, setMetrics] = useState(null);
    const [healthStatus, setHealthStatus] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [timeRange, setTimeRange] = useState('1h');

    useEffect(() => {
        fetchMonitoringData();
        const interval = setInterval(fetchMonitoringData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, [timeRange]);

    const fetchMonitoringData = async () => {
        try {
            setLoading(true);
            const [metricsRes, healthRes, alertsRes] = await Promise.all([
                monitoringAPI.getSystemMetrics(),
                monitoringAPI.getHealthStatus(),
                monitoringAPI.getAlerts({ limit: 10 })
            ]);

            setMetrics(metricsRes.data || {});
            setHealthStatus(healthRes.data || {});
            setAlerts(alertsRes.data || []);
            setError(null);
        } catch (err) {
            setError('Failed to load monitoring data');
            console.error('Error fetching monitoring data:', err);
        } finally {
            setLoading(false);
        }
    };

    // Mock data for charts
    const cpuData = [
        { time: '10:00', usage: 45 },
        { time: '10:15', usage: 52 },
        { time: '10:30', usage: 48 },
        { time: '10:45', usage: 65 },
        { time: '11:00', usage: 58 },
        { time: '11:15', usage: 72 },
        { time: '11:30', usage: 68 },
    ];

    const memoryData = [
        { time: '10:00', usage: 62 },
        { time: '10:15', usage: 65 },
        { time: '10:30', usage: 68 },
        { time: '10:45', usage: 70 },
        { time: '11:00', usage: 67 },
        { time: '11:15', usage: 72 },
        { time: '11:30', usage: 75 },
    ];

    const requestData = [
        { endpoint: '/api/auth', count: 1250 },
        { endpoint: '/api/apps', count: 980 },
        { endpoint: '/api/deploy', count: 450 },
        { endpoint: '/api/metrics', count: 2100 },
        { endpoint: '/api/incidents', count: 320 },
    ];

    if (loading && !metrics) {
        return (
            <div className="page-container">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading monitoring data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">System Monitoring</h1>
                    <p className="page-subtitle">Real-time platform health and performance</p>
                </div>
                <button className="btn-secondary" onClick={fetchMonitoringData}>
                    <RefreshCw size={20} />
                    Refresh
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

            {alerts.length > 0 && (
                <AlertBanner
                    type="warning"
                    message={`${alerts.length} active alerts require attention`}
                    dismissible={false}
                />
            )}

            <div className="metrics-grid">
                <MetricCard
                    title="CPU Usage"
                    value={metrics?.cpu || 68}
                    unit="%"
                    trend="up"
                    trendValue="+5%"
                    icon={Cpu}
                    color="#3b82f6"
                />
                <MetricCard
                    title="Memory Usage"
                    value={metrics?.memory || 75}
                    unit="%"
                    trend="up"
                    trendValue="+3%"
                    icon={HardDrive}
                    color="#8b5cf6"
                />
                <MetricCard
                    title="Active Requests"
                    value={metrics?.requests || 1247}
                    trend="down"
                    trendValue="-12%"
                    icon={Activity}
                    color="#10b981"
                />
                <MetricCard
                    title="Response Time"
                    value={metrics?.responseTime || 145}
                    unit="ms"
                    trend="down"
                    trendValue="-8ms"
                    icon={Zap}
                    color="#f59e0b"
                />
            </div>

            <div className="monitoring-content">
                <div className="monitoring-section full-width">
                    <div className="section-header">
                        <h2 className="section-title">System Health</h2>
                        <div className="health-status">
                            <span className={`health-indicator ${healthStatus?.status || 'healthy'}`}></span>
                            <span className="health-label">{healthStatus?.status || 'Healthy'}</span>
                        </div>
                    </div>
                    <div className="health-grid">
                        <div className="health-item">
                            <span className="health-service">Database</span>
                            <span className="health-badge healthy">Operational</span>
                        </div>
                        <div className="health-item">
                            <span className="health-service">API Server</span>
                            <span className="health-badge healthy">Operational</span>
                        </div>
                        <div className="health-item">
                            <span className="health-service">Cache</span>
                            <span className="health-badge healthy">Operational</span>
                        </div>
                        <div className="health-item">
                            <span className="health-service">Message Queue</span>
                            <span className="health-badge healthy">Operational</span>
                        </div>
                    </div>
                </div>

                <div className="monitoring-section">
                    <div className="section-header">
                        <h2 className="section-title">CPU Usage</h2>
                        <select
                            className="time-range-select"
                            value={timeRange}
                            onChange={(e) => setTimeRange(e.target.value)}
                        >
                            <option value="1h">Last Hour</option>
                            <option value="24h">Last 24 Hours</option>
                            <option value="7d">Last 7 Days</option>
                        </select>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={250}>
                            <AreaChart data={cpuData}>
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
                                <Area
                                    type="monotone"
                                    dataKey="usage"
                                    stroke="#3b82f6"
                                    fill="#3b82f6"
                                    fillOpacity={0.2}
                                    strokeWidth={2}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="monitoring-section">
                    <div className="section-header">
                        <h2 className="section-title">Memory Usage</h2>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={250}>
                            <AreaChart data={memoryData}>
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
                                <Area
                                    type="monotone"
                                    dataKey="usage"
                                    stroke="#8b5cf6"
                                    fill="#8b5cf6"
                                    fillOpacity={0.2}
                                    strokeWidth={2}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="monitoring-section full-width">
                    <div className="section-header">
                        <h2 className="section-title">API Request Distribution</h2>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={requestData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis dataKey="endpoint" stroke="#6b7280" />
                                <YAxis stroke="#6b7280" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#fff',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Bar dataKey="count" fill="#10b981" radius={[8, 8, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Monitoring;