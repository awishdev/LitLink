import pytest
from datetime import datetime, timedelta

# helpers pulled from your existing tests
def register_and_login(client, username='user', password='password123'):
    client.post('/api/auth/register', json={'username': username, 'password': password})
    login = client.post('/api/auth/login', json={'username': username, 'password': password})
    return login.get_json()['access_token']

def create_club(client, token):
    resp = client.post(
        '/api/clubs',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Test Club', 'description': 'Desc'}
    )
    return resp.get_json()

def schedule_meeting(client, token, club_id, date=None, location='Here'):
    d = (date or (datetime.utcnow() + timedelta(days=1))).isoformat()
    resp = client.post(
        f'/api/clubs/{club_id}/meetings',
        headers={'Authorization': f'Bearer {token}'},
        json={'date': d, 'location': location}
    )
    return resp

@pytest.fixture
def token(client, db):
    return register_and_login(client)

@pytest.fixture
def club(client, token):
    return create_club(client, token)

@pytest.fixture
def meeting(client, token, club):
    return schedule_meeting(client, token, club['id']).get_json()

# ——— Tests for ClubComments ———

def test_club_list_comments_empty(client, token, club):
    resp = client.get(f"/api/clubs/{club['id']}/comments")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_club_post_requires_auth(client, club):
    resp = client.post(f"/api/clubs/{club['id']}/comments", json={'content': 'Hi'})
    assert resp.status_code == 401

def test_club_post_and_get(client, token, club):
    post = client.post(
        f"/api/clubs/{club['id']}/comments",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'First!'}
    )
    assert post.status_code == 201
    data = post.get_json()
    assert data['content'] == 'First!'
    # now list
    lst = client.get(f"/api/clubs/{club['id']}/comments")
    assert any(c['id'] == data['id'] for c in lst.get_json())

def test_club_edit_and_delete(client, token, club):
    post = client.post(
        f"/api/clubs/{club['id']}/comments",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'Original'}
    ).get_json()
    # edit
    edit = client.patch(
        f"/api/clubs/{club['id']}/comments/{post['id']}",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'Edited'}
    )
    assert edit.status_code == 200
    assert edit.get_json()['content'] == 'Edited'
    # delete
    dl = client.delete(
        f"/api/clubs/{club['id']}/comments/{post['id']}",
        headers={'Authorization': f'Bearer {token}'}
    )
    assert dl.status_code == 204

def test_club_comment_forbidden(client, token, club):
    post = client.post(
        f"/api/clubs/{club['id']}/comments",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'Mine'}
    ).get_json()

    # another user
    t2 = register_and_login(client, username='other')
    forb = client.patch(
        f"/api/clubs/{club['id']}/comments/{post['id']}",
        headers={'Authorization': f'Bearer {t2}'},
        json={'content': 'Hacked'}
    )
    assert forb.status_code == 403

# ——— Tests for MeetingComments ———

def test_meeting_list_comments_empty(client, token, club, meeting):
    resp = client.get(f"/api/meetings/{meeting['id']}/comments")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_meeting_post_requires_auth(client, meeting):
    resp = client.post(f"/api/meetings/{meeting['id']}/comments", json={'content': 'Hi'})
    assert resp.status_code == 401

def test_meeting_post_and_get(client, token, meeting):
    post = client.post(
        f"/api/meetings/{meeting['id']}/comments",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'Discuss!'}
    )
    assert post.status_code == 201
    data = post.get_json()
    # get
    lst = client.get(f"/api/meetings/{meeting['id']}/comments")
    assert any(c['id'] == data['id'] for c in lst.get_json())

def test_meeting_edit_and_delete(client, token, meeting):
    post = client.post(
        f"/api/meetings/{meeting['id']}/comments",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'A'}
    ).get_json()
    edit = client.patch(
        f"/api/meetings/{meeting['id']}/comments/{post['id']}",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'B'}
    )
    assert edit.status_code == 200
    assert edit.get_json()['content'] == 'B'

    dl = client.delete(
        f"/api/meetings/{meeting['id']}/comments/{post['id']}",
        headers={'Authorization': f'Bearer {token}'}
    )
    assert dl.status_code == 204

def test_meeting_comment_forbidden(client, token, meeting):
    post = client.post(
        f"/api/meetings/{meeting['id']}/comments",
        headers={'Authorization': f'Bearer {token}'},
        json={'content': 'Mine'}
    ).get_json()
    t2 = register_and_login(client, username='other2')
    forb = client.delete(
        f"/api/meetings/{meeting['id']}/comments/{post['id']}",
        headers={'Authorization': f'Bearer {t2}'}
    )
    assert forb.status_code == 403
