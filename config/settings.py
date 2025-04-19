# -*- coding: utf-8 -*-
"""
Application configuration settings.
"""

import os
from pathlib import Path

class Config:
    """Base configuration class."""
    
    # Base directory
    BASE_DIR = Path(__file__).parent.parent
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///orderbyvoice.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Temporary files
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    
    # Audio settings
    AUDIO_UPLOAD_FOLDER = os.getenv('AUDIO_UPLOAD_FOLDER', os.path.join(TEMP_DIR, 'audio'))
    AUDIO_ALLOWED_EXTENSIONS = {'ogg', 'wav', 'mp3'}
    
    # Products and synonyms
    PRODUCTS = {
        "hamburguer": 15.00,
        "pizza": 25.00,
        "refrigerante": 5.00,
        "batata frita": 10.00,
        "sorvete": 8.00
    }
    
    SYNONYMS = {
        "hambúrguer": "hamburguer",
        "pizza": "pizza",
        "refri": "refrigerante",
        "batata": "batata frita",
        "sorvete": "sorvete"
    }
    
    # Speech settings
    SPEECH_RATE = 150
    SPEECH_VOLUME = 0.9

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Speech settings
    SPEECH_LANGUAGE = os.getenv('SPEECH_LANGUAGE', 'pt-BR')
    SPEECH_MODEL = os.getenv('SPEECH_MODEL', 'default')
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
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