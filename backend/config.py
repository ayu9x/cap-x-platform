"""
Configuration management for CAP-X Platform
Loads environment variables and provides centralized configuration access
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # JWT Configuration
    JWT_SECRET_KEY = SECRET_KEY
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=JWT_EXPIRY_HOURS)
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/capx')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'capx')
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_ECR_REGISTRY = os.getenv('AWS_ECR_REGISTRY', '')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'capx-terraform-state')
    
    # Kubernetes Configuration
    KUBERNETES_NAMESPACE = os.getenv('KUBERNETES_NAMESPACE', 'capx-platform')
    KUBECONFIG_PATH = os.getenv('KUBECONFIG_PATH', '')
    IN_CLUSTER = os.getenv('KUBECONFIG_PATH', '').lower() == 'in-cluster'
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_ORG = os.getenv('GITHUB_ORG', '')
    
    # Prometheus Configuration
    PROMETHEUS_URL = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
    PROMETHEUS_PUSHGATEWAY = os.getenv('PROMETHEUS_PUSHGATEWAY', 'http://localhost:9091')
    
    # Grafana Configuration
    GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:3001')
    GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY', '')
    
    # ELK Stack Configuration
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    KIBANA_URL = os.getenv('KIBANA_URL', 'http://localhost:5601')
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    
    # Auto-Healing Configuration
    AUTO_HEALING_ENABLED = os.getenv('AUTO_HEALING_ENABLED', 'True').lower() == 'true'
    HEALTH_CHECK_INTERVAL_SECONDS = int(os.getenv('HEALTH_CHECK_INTERVAL_SECONDS', 60))
    INCIDENT_RETENTION_DAYS = int(os.getenv('INCIDENT_RETENTION_DAYS', 90))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/capx.log')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    # Feature Flags
    ENABLE_AI_INSIGHTS = os.getenv('ENABLE_AI_INSIGHTS', 'True').lower() == 'true'
    ENABLE_TERRAFORM = os.getenv('ENABLE_TERRAFORM', 'True').lower() == 'true'
    ENABLE_AUTO_HEALING = os.getenv('ENABLE_AUTO_HEALING', 'True').lower() == 'true'
    
    # Application Metadata
    APP_NAME = "CAP-X Platform"
    APP_VERSION = "1.0.0"
    API_PREFIX = "/api"
    
    @staticmethod
    def validate():
        """Validate critical configuration values"""
        errors = []
        
        if Config.SECRET_KEY == 'dev-secret-key-change-in-production' and Config.FLASK_ENV == 'production':
            errors.append("SECRET_KEY must be changed in production")
        
        if not Config.MONGO_URI:
            errors.append("MONGO_URI is required")
        
        if Config.ENABLE_TERRAFORM and not Config.AWS_ACCESS_KEY_ID:
            errors.append("AWS credentials required when Terraform is enabled")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @staticmethod
    def get_database_name():
        """Extract database name from MongoDB URI"""
        if '/' in Config.MONGO_URI:
            return Config.MONGO_URI.split('/')[-1].split('?')[0]
        return Config.MONGO_DB_NAME


# Validate configuration on import
if os.getenv('SKIP_CONFIG_VALIDATION', 'False').lower() != 'true':
    try:
        Config.validate()
    except ValueError as e:
        print(f"⚠️  Configuration Warning: {e}")
