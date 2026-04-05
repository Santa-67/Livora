import sys
import os
import pytest
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from flask import json
import os
import tempfile
from datetime import datetime, UTC

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
    # Properly close DB before deleting file
    with app.app_context():
        db.session.remove()
        db.engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)

def test_signup_and_login(client):
    # Signup
    response = client.post('/auth/signup', json={
        'email': 'testuser@example.com',
        'password': 'TestPass123',
        'name': 'Test User'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['user']['email'] == 'testuser@example.com'

    # Login
    response = client.post('/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'TestPass123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
