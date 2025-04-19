# -*- coding: utf-8 -*-
"""
Order by Voice - Main Application
A Flask-based application for voice-based order processing.
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from src.config.settings import Config
from src.api.routes import register_routes
from src.cli import init_app as init_cli

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
    
    # Register routes
    register_routes(app)
    
    # Register CLI commands
    init_cli(app)
    
    # Create necessary directories
    os.makedirs(app.config['TEMP_DIR'], exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 