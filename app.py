# -*- coding: utf-8 -*-
"""
Order by Voice - Main Application
A Flask-based application for voice-based order processing.
"""

import os
import click
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config.settings import Config
from controllers.pedidos import pedidos_bp
from controllers.clientes import clientes_bp
from core.database import init_db

# Initialize extensions
db = SQLAlchemy()

def create_app(config_class=Config):
    """
    Create and configure the Flask application.
    
    Args:
        config_class: Configuration class to use for the application
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(pedidos_bp, url_prefix='/api/v1')
    app.register_blueprint(clientes_bp, url_prefix='/api/v1')
    
    # Create necessary directories
    os.makedirs(app.config['TEMP_DIR'], exist_ok=True)
    
    # Register CLI commands
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        init_db()
        click.echo('Initialized the database.')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
