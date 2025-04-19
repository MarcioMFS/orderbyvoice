# -*- coding: utf-8 -*-
"""
Database core module for handling database connections and operations.
"""

import os
import sqlite3
from typing import Optional
from flask import current_app, g

def get_db() -> sqlite3.Connection:
    """
    Get a database connection.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    if 'db' not in g:
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        current_app.logger.info(f"Connecting to database at: {db_path}")
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e: Optional[Exception] = None) -> None:
    """
    Close the database connection.
    
    Args:
        e: Optional exception that triggered the close
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db() -> None:
    """
    Initialize the database with required tables.
    """
    db = get_db()
    
    try:
        schema_path = os.path.join(current_app.root_path, 'schema.sql')
        current_app.logger.info(f"Reading schema from: {schema_path}")
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
            current_app.logger.info("Executing schema:")
            current_app.logger.info(schema)
            db.executescript(schema)
            db.commit()
            current_app.logger.info("Database initialized successfully")
            
    except Exception as e:
        current_app.logger.error(f"Error initializing database: {e}")
        raise

def init_app(app) -> None:
    """
    Initialize the database for the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def init_db_command():
    """
    CLI command to initialize the database.
    """
    init_db()
    print('Initialized the database.') 