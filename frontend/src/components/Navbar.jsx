import { Bell, Search, User, ChevronDown } from 'lucide-react';
import { useState } from 'react';

const Navbar = () => {
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [notifications, setNotifications] = useState(3);

    return (
        <nav className="navbar">
            <div className="navbar-search">
                <Search size={20} className="search-icon" />
                <input
                    type="text"
                    placeholder="Search applications, deployments, incidents..."
                    className="search-input"
                />
            </div>

            <div className="navbar-actions">
                <button className="navbar-btn notification-btn">
                    <Bell size={20} />
                    {notifications > 0 && (
                        <span className="notification-badge">{notifications}</span>
                    )}
                </button>

                <div className="user-menu">
                    <button
                        className="user-menu-btn"
                        onClick={() => setShowUserMenu(!showUserMenu)}
                    >
                        <div className="user-avatar">
                            <User size={18} />
                        </div>
                        <span className="user-name">Admin User</span>
                        <ChevronDown size={16} />
                    </button>

                    {showUserMenu && (
                        <div className="user-dropdown">
                            <div className="dropdown-item">
                                <User size={16} />
                                <span>Profile</span>
                            </div>
                            <div className="dropdown-item">
                                <span>Settings</span>
                            </div>
                            <div className="dropdown-divider"></div>
                            <div className="dropdown-item logout">
                                <span>Logout</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;