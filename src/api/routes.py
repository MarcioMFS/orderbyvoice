"""
API routes registration.
"""

from flask import Blueprint, send_from_directory, jsonify
from .controllers import pedidos_bp, clientes_bp

def register_routes(app):
    """
    Register all API routes with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Create API blueprint
    api_bp = Blueprint('api', __name__, url_prefix=app.config['API_PREFIX'])
    
    # Register blueprints
    api_bp.register_blueprint(pedidos_bp)
    api_bp.register_blueprint(clientes_bp)
    
    # Register API blueprint with app
    app.register_blueprint(api_bp)
    
    # Register static file serving
    @app.route('/interface_teste/<path:path>')
    def serve_interface(path):
        return send_from_directory('interface_teste', path)
    
    # Register root route
    @app.route('/')
    def home():
        return jsonify({
            "message": "Bem-vindo à API de Pedidos por Voz!",
            "version": "1.0.0",
            "docs": "/docs"  # TODO: Add API documentation endpoint
        }), 200 