import pytest
from datetime import datetime, timedelta

# Helpers
def register_and_login(client, username='testuser', password='password123'):
    # Register
    r = client.post('/api/auth/register', json={
        'username': username,
        'password': password
    })
    assert r.status_code == 201

    # Login
    r = client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })
    assert r.status_code == 200
    return r.get_json()['access_token']

def create_club(client, token, name='My Club', description='Just a club'):
    r = client.post(
        '/api/clubs',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': name, 'description': description}
    )
    assert r.status_code == 201
    return r.get_json()

def schedule_meeting(client, token, club_id, date=None, location='Library', book_id=None):
    payload = {}
    if date is not None:
        payload['date'] = date.isoformat()
    payload['location'] = location
    if book_id is not None:
        payload['book_id'] = book_id

    return client.post(
        f'/api/clubs/{club_id}/meetings',
        headers={'Authorization': f'Bearer {token}'},
        json=payload
    )

# Tests

def test_list_meetings_empty(client, db):
    token = register_and_login(client)
    club = create_club(client, token)
    resp = client.get(f'/api/clubs/{club["id"]}/meetings')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_meeting_requires_auth(client, db):
    token = register_and_login(client)
    club = create_club(client, token)

    # No auth header
    resp = client.post(f'/api/clubs/{club["id"]}/meetings', json={
        'date': datetime.utcnow().isoformat(),
        'location': 'Library'
    })
    assert resp.status_code == 401


@pytest.mark.parametrize("payload,missing_field", [
    ({'location': 'Library'}, 'date'),
    ({'date': datetime.utcnow().isoformat()}, 'location'),
])
def test_create_meeting_missing_fields(client, db, payload, missing_field):
    token = register_and_login(client)
    club = create_club(client, token)
    resp = client.post(
        f'/api/clubs/{club["id"]}/meetings',
        headers={'Authorization': f'Bearer {token}'},
        json=payload
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert missing_field in body['message'] or missing_field in body['errors']


def test_create_meeting_invalid_date(client, db):
    token = register_and_login(client)
    club = create_club(client, token)
    # send a bad date format
    resp = client.post(
        f'/api/clubs/{club["id"]}/meetings',
        headers={'Authorization': f'Bearer {token}'},
        json={'date': 'not-a-date', 'location': 'Library'}
    )
    assert resp.status_code == 400
    assert 'date' in resp.get_json()['message']


def test_create_and_get_meeting(client, db):
    token = register_and_login(client)
    club = create_club(client, token)

    meet_time = datetime.utcnow() + timedelta(days=1)
    create_resp = schedule_meeting(client, token, club['id'], date=meet_time, location='Library')
    assert create_resp.status_code == 201
    meeting = create_resp.get_json()
    assert meeting['location'] == 'Library'
    assert 'date' in meeting

    # fetch detail
    get_resp = client.get(f'/api/meetings/{meeting["id"]}')
    assert get_resp.status_code == 200
    fetched = get_resp.get_json()
    assert fetched == meeting


def test_update_meeting(client, db):
    token = register_and_login(client)
    club = create_club(client, token)

    meet_time = datetime.utcnow() + timedelta(days=2)
    meeting = schedule_meeting(client, token, club['id'], date=meet_time, location='Library').get_json()

    # patch location and date
    new_time = meet_time + timedelta(days=1)
    patch_resp = client.patch(
        f'/api/meetings/{meeting["id"]}',
        headers={'Authorization': f'Bearer {token}'},
        json={'location': 'Cafe', 'date': new_time.isoformat()}
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.get_json()
    assert updated['location'] == 'Cafe'
    assert updated['date'].startswith(new_time.isoformat()[:19])


def test_delete_meeting(client, db):
    token = register_and_login(client)
    club = create_club(client, token)

    meet_time = datetime.utcnow() + timedelta(days=3)
    meeting = schedule_meeting(client, token, club['id'], date=meet_time, location='Library').get_json()

    del_resp = client.delete(
        f'/api/meetings/{meeting["id"]}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert del_resp.status_code == 204

    # now 404 on detail
    assert client.get(f'/api/meetings/{meeting["id"]}').status_code == 404
