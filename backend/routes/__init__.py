"""
Routes package for CAP-X Platform
Exports all route blueprints
"""

from .auth import auth_bp
from .apps import apps_bp
from .deployments import deployments_bp
from .pipelines import pipelines_bp
from .monitoring import monitoring_bp
from .incidents import incidents_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'apps_bp',
    'deployments_bp',
    'pipelines_bp',
    'monitoring_bp',
    'incidents_bp',
    'admin_bp'
]