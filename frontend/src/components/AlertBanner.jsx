import { AlertTriangle, CheckCircle, Info, XCircle, X } from 'lucide-react';
import { useState } from 'react';

const AlertBanner = ({ type = 'info', message, dismissible = true, onDismiss }) => {
    const [isVisible, setIsVisible] = useState(true);

    const alertConfig = {
        success: {
            icon: CheckCircle,
            className: 'alert-success',
            iconColor: '#10b981'
        },
        error: {
            icon: XCircle,
            className: 'alert-error',
            iconColor: '#ef4444'
        },
        warning: {
            icon: AlertTriangle,
            className: 'alert-warning',
            iconColor: '#f59e0b'
        },
        info: {
            icon: Info,
            className: 'alert-info',
            iconColor: '#3b82f6'
        }
    };

    const config = alertConfig[type] || alertConfig.info;
    const Icon = config.icon;

    const handleDismiss = () => {
        setIsVisible(false);
        if (onDismiss) {
            onDismiss();
        }
    };

    if (!isVisible) return null;

    return (
        <div className={`alert-banner ${config.className}`}>
            <div className="alert-content">
                <Icon size={20} color={config.iconColor} />
                <span className="alert-message">{message}</span>
            </div>
            {dismissible && (
                <button className="alert-dismiss" onClick={handleDismiss}>
                    <X size={18} />
                </button>
            )}
        </div>
    );
};

export default AlertBanner;
