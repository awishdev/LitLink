import pytest

def register_user(client, username='testuser', password='password123'):
    return client.post(
        '/api/auth/register',
        json={'username': username, 'password': password}
    )

def login_user(client, username='testuser', password='password123'):
    resp = client.post(
        '/api/auth/login',
        json={'username': username, 'password': password}
    )
    return resp.get_json()['access_token']

def create_club(client, token, name='Test Club', description='A club'):
    resp = client.post(
        '/api/clubs',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': name, 'description': description}
    )
    return resp.get_json()


def test_list_members_empty(client, db):
    register_user(client)
    token = login_user(client)

    club = create_club(client, token)
    resp = client.get(f"/api/clubs/{club['id']}/memberships")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_join_club_requires_auth(client, db):
    register_user(client)
    token = login_user(client)

    club = create_club(client, token)
    # no Authorization header:
    resp = client.post(f"/api/clubs/{club['id']}/memberships")
    assert resp.status_code == 401


def test_join_and_duplicate(client, db):
    register_user(client)
    token = login_user(client)

    club = create_club(client, token)

    # first join
    resp = client.post(
        f"/api/clubs/{club['id']}/memberships",
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    m = resp.get_json()
    assert m['club_id'] == club['id']
    assert m['user_id']  # should be the user's id

    # duplicate join
    resp2 = client.post(
        f"/api/clubs/{club['id']}/memberships",
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp2.status_code == 400


def test_leave_and_forbidden(client, db):
    # user1 signs up, creates club & joins
    register_user(client)
    token1 = login_user(client)
    club = create_club(client, token1)

    resp = client.post(
        f"/api/clubs/{club['id']}/memberships",
        headers={'Authorization': f'Bearer {token1}'}
    )
    membership_id = resp.get_json()['id']

    # user2 tries to leave user1's membership
    register_user(client, username='other', password='password123')
    token2 = login_user(client, username='other', password='password123')
    resp_forbid = client.delete(
        f"/api/clubs/{club['id']}/memberships/{membership_id}",
        headers={'Authorization': f'Bearer {token2}'}
    )
    assert resp_forbid.status_code == 403

    # rightful leave by user1
    resp_leave = client.delete(
        f"/api/clubs/{club['id']}/memberships/{membership_id}",
        headers={'Authorization': f'Bearer {token1}'}
    )
    assert resp_leave.status_code == 204

    # back to zero members
    resp_list = client.get(f"/api/clubs/{club['id']}/memberships")
    assert resp_list.status_code == 200
    assert resp_list.get_json() == []


def test_update_role(client, db):
    register_user(client)
    token = login_user(client)

    club = create_club(client, token)
    resp = client.post(
        f"/api/clubs/{club['id']}/memberships",
        headers={'Authorization': f'Bearer {token}'}
    )
    m_id = resp.get_json()['id']

    resp_patch = client.patch(
        f"/api/clubs/{club['id']}/memberships/{m_id}",
        headers={'Authorization': f'Bearer {token}'},
        json={'role': 'admin'}
    )
    assert resp_patch.status_code == 200
    assert resp_patch.get_json()['role'] == 'admin'


def test_update_role_forbidden(client, db):
    # set up user1
    register_user(client)
    token1 = login_user(client)
    club = create_club(client, token1)

    resp = client.post(
        f"/api/clubs/{club['id']}/memberships",
        headers={'Authorization': f'Bearer {token1}'}
    )
    m_id = resp.get_json()['id']

    # user2 tries to change user1’s role
    register_user(client, username='other', password='password123')
    token2 = login_user(client, username='other', password='password123')
    resp_forbid = client.patch(
        f"/api/clubs/{club['id']}/memberships/{m_id}",
        headers={'Authorization': f'Bearer {token2}'},
        json={'role': 'moderator'}
    )
    assert resp_forbid.status_code == 403
