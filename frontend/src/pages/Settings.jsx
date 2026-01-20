import { useState, useEffect } from 'react';
import { User, Bell, Key, Shield, Save } from 'lucide-react';
import { settingsAPI } from '../services/api';
import AlertBanner from '../components/AlertBanner';

const Settings = () => {
    const [activeTab, setActiveTab] = useState('profile');
    const [profile, setProfile] = useState({
        name: '',
        email: '',
        role: '',
    });
    const [notifications, setNotifications] = useState({
        emailNotifications: true,
        deploymentAlerts: true,
        incidentAlerts: true,
        weeklyReports: false,
    });
    const [apiKeys, setApiKeys] = useState([]);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchSettings();
    }, [activeTab]);

    const fetchSettings = async () => {
        try {
            setLoading(true);
            if (activeTab === 'profile') {
                const response = await settingsAPI.getProfile();
                setProfile(response.data || {});
            } else if (activeTab === 'notifications') {
                const response = await settingsAPI.getNotificationSettings();
                setNotifications(response.data || {});
            } else if (activeTab === 'api-keys') {
                const response = await settingsAPI.getAPIKeys();
                setApiKeys(response.data || []);
            }
        } catch (err) {
            console.error('Error fetching settings:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSaveProfile = async () => {
        try {
            await settingsAPI.updateProfile(profile);
            setSuccess('Profile updated successfully');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError('Failed to update profile');
            console.error('Error updating profile:', err);
        }
    };

    const handleSaveNotifications = async () => {
        try {
            await settingsAPI.updateNotificationSettings(notifications);
            setSuccess('Notification settings updated');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError('Failed to update notification settings');
            console.error('Error updating notifications:', err);
        }
    };

    const handleCreateAPIKey = async () => {
        try {
            const response = await settingsAPI.createAPIKey({ name: 'New API Key' });
            setApiKeys([...apiKeys, response.data]);
            setSuccess('API key created successfully');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError('Failed to create API key');
            console.error('Error creating API key:', err);
        }
    };

    const handleRevokeAPIKey = async (keyId) => {
        try {
            await settingsAPI.revokeAPIKey(keyId);
            setApiKeys(apiKeys.filter(key => key.id !== keyId));
            setSuccess('API key revoked');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError('Failed to revoke API key');
            console.error('Error revoking API key:', err);
        }
    };

    const tabs = [
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'api-keys', label: 'API Keys', icon: Key },
        { id: 'security', label: 'Security', icon: Shield },
    ];

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="header-content">
                    <h1 className="page-title">Settings</h1>
                    <p className="page-subtitle">Manage your account and preferences</p>
                </div>
            </div>

            {success && (
                <AlertBanner
                    type="success"
                    message={success}
                    dismissible={true}
                    onDismiss={() => setSuccess(null)}
                />
            )}

            {error && (
                <AlertBanner
                    type="error"
                    message={error}
                    dismissible={true}
                    onDismiss={() => setError(null)}
                />
            )}

            <div className="settings-container">
                <div className="settings-tabs">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                <Icon size={20} />
                                <span>{tab.label}</span>
                            </button>
                        );
                    })}
                </div>

                <div className="settings-content">
                    {activeTab === 'profile' && (
                        <div className="settings-section">
                            <h2 className="section-title">Profile Information</h2>
                            <div className="form-group">
                                <label className="form-label">Full Name</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={profile.name}
                                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                                    placeholder="Enter your name"
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Email Address</label>
                                <input
                                    type="email"
                                    className="form-input"
                                    value={profile.email}
                                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                    placeholder="Enter your email"
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Role</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={profile.role}
                                    disabled
                                    placeholder="Your role"
                                />
                            </div>
                            <button className="btn-primary" onClick={handleSaveProfile}>
                                <Save size={20} />
                                Save Changes
                            </button>
                        </div>
                    )}

                    {activeTab === 'notifications' && (
                        <div className="settings-section">
                            <h2 className="section-title">Notification Preferences</h2>
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        checked={notifications.emailNotifications}
                                        onChange={(e) => setNotifications({ ...notifications, emailNotifications: e.target.checked })}
                                    />
                                    <span>Email Notifications</span>
                                </label>
                                <p className="form-help">Receive email notifications for important events</p>
                            </div>
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        checked={notifications.deploymentAlerts}
                                        onChange={(e) => setNotifications({ ...notifications, deploymentAlerts: e.target.checked })}
                                    />
                                    <span>Deployment Alerts</span>
                                </label>
                                <p className="form-help">Get notified about deployment status changes</p>
                            </div>
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        checked={notifications.incidentAlerts}
                                        onChange={(e) => setNotifications({ ...notifications, incidentAlerts: e.target.checked })}
                                    />
                                    <span>Incident Alerts</span>
                                </label>
                                <p className="form-help">Receive alerts for new and critical incidents</p>
                            </div>
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        checked={notifications.weeklyReports}
                                        onChange={(e) => setNotifications({ ...notifications, weeklyReports: e.target.checked })}
                                    />
                                    <span>Weekly Reports</span>
                                </label>
                                <p className="form-help">Get weekly summary reports via email</p>
                            </div>
                            <button className="btn-primary" onClick={handleSaveNotifications}>
                                <Save size={20} />
                                Save Preferences
                            </button>
                        </div>
                    )}

                    {activeTab === 'api-keys' && (
                        <div className="settings-section">
                            <div className="section-header">
                                <h2 className="section-title">API Keys</h2>
                                <button className="btn-primary" onClick={handleCreateAPIKey}>
                                    <Key size={20} />
                                    Generate New Key
                                </button>
                            </div>
                            <p className="section-description">
                                API keys allow you to authenticate with the CAP-X API programmatically
                            </p>
                            <div className="api-keys-list">
                                {apiKeys.length > 0 ? (
                                    apiKeys.map((key) => (
                                        <div key={key.id} className="api-key-item">
                                            <div className="api-key-info">
                                                <span className="api-key-name">{key.name}</span>
                                                <code className="api-key-value">{key.key}</code>
                                                <span className="api-key-created">Created: {key.createdAt}</span>
                                            </div>
                                            <button
                                                className="btn-danger btn-sm"
                                                onClick={() => handleRevokeAPIKey(key.id)}
                                            >
                                                Revoke
                                            </button>
                                        </div>
                                    ))
                                ) : (
                                    <div className="empty-state-small">
                                        <Key size={48} color="#9ca3af" />
                                        <p>No API keys created yet</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'security' && (
                        <div className="settings-section">
                            <h2 className="section-title">Security Settings</h2>
                            <div className="form-group">
                                <label className="form-label">Current Password</label>
                                <input
                                    type="password"
                                    className="form-input"
                                    placeholder="Enter current password"
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">New Password</label>
                                <input
                                    type="password"
                                    className="form-input"
                                    placeholder="Enter new password"
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Confirm New Password</label>
                                <input
                                    type="password"
                                    className="form-input"
                                    placeholder="Confirm new password"
                                />
                            </div>
                            <button className="btn-primary">
                                <Shield size={20} />
                                Update Password
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Settings;