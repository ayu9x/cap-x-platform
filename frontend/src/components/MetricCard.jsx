import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const MetricCard = ({ title, value, unit, trend, trendValue, icon: Icon, color = '#3b82f6' }) => {
    const getTrendIcon = () => {
        if (trend === 'up') return TrendingUp;
        if (trend === 'down') return TrendingDown;
        return Minus;
    };

    const getTrendClass = () => {
        if (trend === 'up') return 'trend-up';
        if (trend === 'down') return 'trend-down';
        return 'trend-neutral';
    };

    const TrendIcon = getTrendIcon();

    return (
        <div className="metric-card">
            <div className="metric-header">
                <div className="metric-icon" style={{ backgroundColor: `${color}20` }}>
                    {Icon && <Icon size={24} color={color} />}
                </div>
                <div className={`metric-trend ${getTrendClass()}`}>
                    <TrendIcon size={16} />
                    <span>{trendValue}</span>
                </div>
            </div>

            <div className="metric-body">
                <h3 className="metric-title">{title}</h3>
                <div className="metric-value-container">
                    <span className="metric-value">{value}</span>
                    {unit && <span className="metric-unit">{unit}</span>}
                </div>
            </div>

            <div className="metric-footer">
                <span className="metric-label">vs last period</span>
            </div>
        </div>
    );
};

export default MetricCard;
