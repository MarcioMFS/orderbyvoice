"""
Database initialization and connection handling.
"""

import sqlite3
from flask import g

def get_db():
    """
    Get database connection from the application context.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Close database connection.
    
    Args:
        e: Exception if any
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """
    Initialize database with the application.
    
    Args:
        app: Flask application instance
    """
    app.teardown_appcontext(close_db)
    
    # Create tables if they don't exist
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8')) 