# -*- coding: utf-8 -*-
"""
CLI commands for the Order by Voice application.
"""

import click
from flask.cli import with_appcontext
from flask import current_app
from core.database import get_db

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    try:
        db = get_db()
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
        click.echo('Database initialized successfully.')
    except Exception as e:
        click.echo(f'Error initializing database: {e}', err=True)

def init_app(app):
    """Register CLI commands with the app."""
    app.cli.add_command(init_db_command) 