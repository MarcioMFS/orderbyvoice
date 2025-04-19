"""
Basic tests for the Order by Voice application.
"""

import os
import tempfile
import pytest
from src.app import create_app
from src.core.database import get_db, init_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE_PATH': db_path,
        'SPEECH_LANGUAGE': 'pt-BR',
        'SPEECH_MODEL': 'default'
    })

    # Create the database and load test data
    with app.app_context():
        init_db(app)

    yield app

    # Clean up the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def test_home_page(client):
    """Test that the home page shows a welcome message."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Bem-vindo' in response.data

def test_create_cliente(client):
    """Test creating a new client."""
    response = client.post('/api/v1/clientes', json={
        'nome': 'Test User',
        'telefone': '11999999999',
        'endereco': 'Test Address'
    })
    assert response.status_code == 201
    assert b'Cliente criado com sucesso' in response.data

def test_init_db_command(runner):
    """Test the init-db command."""
    result = runner.invoke(args=['init-db'])
    assert 'Database initialized successfully' in result.output 