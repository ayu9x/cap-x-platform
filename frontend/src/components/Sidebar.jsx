import { Link, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    Package,
    Rocket,
    AlertTriangle,
    GitBranch,
    Activity,
    Settings,
    LogOut
} from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();

    const menuItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/applications', icon: Package, label: 'Applications' },
        { path: '/deployments', icon: Rocket, label: 'Deployments' },
        { path: '/incidents', icon: AlertTriangle, label: 'Incidents' },
        { path: '/pipelines', icon: GitBranch, label: 'Pipelines' },
        { path: '/monitoring', icon: Activity, label: 'Monitoring' },
    ];

    const isActive = (path) => {
        return location.pathname === path;
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <h1 className="sidebar-logo">CAP-X</h1>
                <p className="sidebar-subtitle">Cloud Platform</p>
            </div>

            <nav className="sidebar-nav">
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`sidebar-link ${isActive(item.path) ? 'active' : ''}`}
                        >
                            <Icon size={20} />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="sidebar-footer">
                <Link to="/settings" className="sidebar-link">
                    <Settings size={20} />
                    <span>Settings</span>
                </Link>
                <button className="sidebar-link logout-btn">
                    <LogOut size={20} />
                    <span>Logout</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
