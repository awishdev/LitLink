import json
import pytest
from app.models import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

def register_user(client):
    return client.post('/api/auth/register',
        json={'username': 'testuser', 'password': 'password123'}
    )

def login_user(client):
    resp = client.post('/api/auth/login',
        json={'username': 'testuser', 'password': 'password123'}
    )
    data = resp.get_json()
    return data['access_token']

def test_club_crud_public(client, db):
    # no clubs yet
    resp = client.get('/api/clubs')
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_create_club_requires_auth(client, db):
    # without token
    resp = client.post('/api/clubs', json={'name': 'Test Club'})
    assert resp.status_code == 401

def test_create_and_get_club(client, db):
    register_user(client)
    token = login_user(client)

    # create a club
    resp = client.post(
        '/api/clubs',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Lambda Readers', 'description': 'A fun club'}
    )
    assert resp.status_code == 201
    club = resp.get_json()
    assert club['name'] == 'Lambda Readers'

    # retrieve it
    resp2 = client.get(f"/api/clubs/{club['id']}")
    assert resp2.status_code == 200
    assert resp2.get_json()['description'] == 'A fun club'
