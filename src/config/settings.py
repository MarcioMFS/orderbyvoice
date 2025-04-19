# -*- coding: utf-8 -*-
"""
Application settings and configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getenv('DATABASE_PATH', 'orderbyvoice.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Speech settings
    SPEECH_LANGUAGE = os.getenv('SPEECH_LANGUAGE', 'pt-BR')
    SPEECH_MODEL = os.getenv('SPEECH_MODEL', 'default')
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # File paths
    TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
    
    # API settings
    API_PREFIX = '/api/v1'
    
    # ChatGPT settings
    CHATGPT_MODEL = os.getenv('CHATGPT_MODEL', 'gpt-3.5-turbo')
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration."""
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Configure logging
        file_handler = RotatingFileHandler(
            'logs/orderbyvoice.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Order by Voice startup')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 