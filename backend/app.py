"""
CAP-X Platform - Main Flask Application
Enterprise-Grade Internal Developer Platform with AI-Assisted Operations
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from prometheus_flask_exporter import PrometheusMetrics

from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE) if os.path.exists(os.path.dirname(Config.LOG_FILE) or '.') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('capx_app_info', 'CAP-X Platform Information', version=Config.APP_VERSION)

# MongoDB connection
mongo_client = None
db = None

def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, db
    try:
        mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        mongo_client.admin.command('ping')
        db = mongo_client[Config.get_database_name()]
        logger.info(f"✅ Connected to MongoDB: {Config.get_database_name()}")
        
        # Create indexes
        create_indexes()
        
        return db
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {str(e)}")
        logger.warning("⚠️  Application will start but database operations will fail")
        return None

def create_indexes():
    """Create database indexes for performance"""
    try:
        # Users collection indexes
        db.users.create_index("email", unique=True)
        db.users.create_index("username", unique=True)
        
        # Applications collection indexes
        db.applications.create_index("name", unique=True)
        db.applications.create_index("status")
        
        # Deployments collection indexes
        db.deployments.create_index([("created_at", -1)])
        db.deployments.create_index("application_id")
        db.deployments.create_index("status")
        
        # Incidents collection indexes
        db.incidents.create_index([("created_at", -1)])
        db.incidents.create_index("status")
        db.incidents.create_index("severity")
        
        # Pipelines collection indexes
        db.pipelines.create_index([("created_at", -1)])
        db.pipelines.create_index("status")
        
        # Audit logs collection indexes
        db.audit_logs.create_index([("timestamp", -1)])
        db.audit_logs.create_index("user_id")
        
        logger.info("✅ Database indexes created successfully")
    except Exception as e:
        logger.warning(f"⚠️  Index creation warning: {str(e)}")

# Initialize database
init_mongodb()

# JWT Authentication Middleware
def token_required(f):
    """Decorator to require JWT token for protected routes"""
    from functools import wraps
    import jwt
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = db.users.find_one({'_id': data['user_id']})
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({'error': 'Token validation failed'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Make token_required available globally
app.token_required = token_required

# Register blueprints/routes
def register_routes():
    """Register all API routes"""
    try:
        from routes import auth, apps, deployments, incidents, monitoring, pipelines, admin
        
        # Register blueprints with API prefix
        app.register_blueprint(auth.bp, url_prefix=f'{Config.API_PREFIX}/auth')
        app.register_blueprint(apps.bp, url_prefix=f'{Config.API_PREFIX}/applications')
        app.register_blueprint(deployments.bp, url_prefix=f'{Config.API_PREFIX}/deployments')
        app.register_blueprint(incidents.bp, url_prefix=f'{Config.API_PREFIX}/incidents')
        app.register_blueprint(monitoring.bp, url_prefix=f'{Config.API_PREFIX}/monitoring')
        app.register_blueprint(pipelines.bp, url_prefix=f'{Config.API_PREFIX}/pipelines')
        app.register_blueprint(admin.bp, url_prefix=f'{Config.API_PREFIX}/admin')
        
        logger.info("✅ All routes registered successfully")
    except Exception as e:
        logger.error(f"❌ Route registration failed: {str(e)}")
        logger.warning("⚠️  Some routes may not be available")

register_routes()

# Root endpoint
@app.route('/')
def index():
    """Root endpoint - API information"""
    return jsonify({
        'name': Config.APP_NAME,
        'version': Config.APP_VERSION,
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'auth': f'{Config.API_PREFIX}/auth',
            'applications': f'{Config.API_PREFIX}/applications',
            'deployments': f'{Config.API_PREFIX}/deployments',
            'incidents': f'{Config.API_PREFIX}/incidents',
            'monitoring': f'{Config.API_PREFIX}/monitoring',
            'pipelines': f'{Config.API_PREFIX}/pipelines',
            'admin': f'{Config.API_PREFIX}/admin',
            'health': '/health',
            'metrics': '/metrics'
        }
    })

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': Config.APP_VERSION,
        'checks': {}
    }
    
    # Check MongoDB connection
    try:
        if mongo_client:
            mongo_client.admin.command('ping')
            health_status['checks']['mongodb'] = 'healthy'
        else:
            health_status['checks']['mongodb'] = 'disconnected'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['mongodb'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

# Dashboard stats endpoint
@app.route(f'{Config.API_PREFIX}/dashboard/stats')
@token_required
def dashboard_stats(current_user):
    """Get dashboard statistics"""
    try:
        stats = {
            'overview': {
                'total_applications': db.applications.count_documents({}),
                'active_applications': db.applications.count_documents({'status': 'active'}),
                'total_deployments': db.deployments.count_documents({}),
                'open_incidents': db.incidents.count_documents({'status': {'$in': ['open', 'investigating']}}),
                'total_users': db.users.count_documents({})
            },
            'deployments': {
                'total': db.deployments.count_documents({}),
                'success': db.deployments.count_documents({'status': 'success'}),
                'failed': db.deployments.count_documents({'status': 'failed'}),
                'in_progress': db.deployments.count_documents({'status': 'in_progress'}),
                'success_rate': 0
            },
            'incidents': {
                'total': db.incidents.count_documents({}),
                'open': db.incidents.count_documents({'status': 'open'}),
                'resolved': db.incidents.count_documents({'status': 'resolved'}),
                'critical': db.incidents.count_documents({'severity': 'critical'}),
                'avg_mttr_minutes': 0
            },
            'pipelines': {
                'total': db.pipelines.count_documents({}),
                'running': db.pipelines.count_documents({'status': 'running'}),
                'success': db.pipelines.count_documents({'status': 'success'}),
                'failed': db.pipelines.count_documents({'status': 'failed'})
            }
        }
        
        # Calculate success rate
        if stats['deployments']['total'] > 0:
            stats['deployments']['success_rate'] = round(
                (stats['deployments']['success'] / stats['deployments']['total']) * 100, 2
            )
        
        # Calculate average MTTR (Mean Time To Resolve)
        resolved_incidents = list(db.incidents.find({'status': 'resolved', 'resolved_at': {'$exists': True}}))
        if resolved_incidents:
            total_resolution_time = sum([
                (inc.get('resolved_at') - inc.get('created_at')).total_seconds() / 60
                for inc in resolved_incidents
                if inc.get('resolved_at') and inc.get('created_at')
            ])
            stats['incidents']['avg_mttr_minutes'] = round(total_resolution_time / len(resolved_incidents), 2)
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard stats'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Request logging middleware
@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log all outgoing responses"""
    logger.info(f"{request.method} {request.path} - {response.status_code}")
    return response

# Cleanup on shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    """Cleanup resources on shutdown"""
    if exception:
        logger.error(f"Application context teardown error: {str(exception)}")

if __name__ == '__main__':
    logger.info(f"🚀 Starting {Config.APP_NAME} v{Config.APP_VERSION}")
    logger.info(f"🌍 Environment: {Config.FLASK_ENV}")
    logger.info(f"🔧 Debug Mode: {Config.DEBUG}")
    logger.info(f"📊 Prometheus metrics available at /metrics")
    logger.info(f"💚 Health check available at /health")
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Run the application
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True
    )