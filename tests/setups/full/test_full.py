from fastapi.testclient import TestClient
import pytest

from .setup import app, enc_acc, enc_ref


@pytest.fixture
def client():
    return TestClient(app)


def test_public(client):
    r1 = client.get('/public')
        
    assert r1.status_code == 200


def test_public_cycle(client):
    r = client.post('/login')
    assert r.status_code == 200

    r = client.get('/public')
    assert r.status_code == 200
    assert 'x-refreshed-access-token' in set(r.headers.keys())
    at = r.headers.get('x-refreshed-access-token')

    r = client.get('/public', headers={'Authorization': at})
    assert r.status_code == 200
    assert 'x-refreshed-access-token' not in set(r.headers.keys())


def test_auth_cycle(client):
    r = client.post('/login')
    assert r.status_code == 200

    r = client.get('/auth')
    assert r.status_code == 200
    assert 'x-refreshed-access-token' in set(r.headers.keys())
    at = r.headers.get('x-refreshed-access-token')

    r = client.get('/auth', headers={'Authorization': at})
    assert r.status_code == 200
    assert 'x-refreshed-access-token' not in set(r.headers.keys())


def test_auth_403(client):
    r = client.post('/login')
    assert r.status_code == 200

    r = client.get('/auth')
    assert r.status_code == 200
    assert 'x-refreshed-access-token' in set(r.headers.keys())
    at = r.headers.get('x-refreshed-access-token')

    r = client.get('/admin', headers={'Authorization': at})
    assert r.status_code == 403
    assert 'x-refreshed-access-token' not in set(r.headers.keys())


def test_admin(client):
    r = client.post('/login?scopes=admin')
    assert r.status_code == 200

    r = client.get('/tester')
    assert r.status_code == 200
    assert 'x-refreshed-access-token' in set(r.headers.keys())
    at = r.headers.get('x-refreshed-access-token')

    r = client.get('/admin', headers={'Authorization': at})
    assert r.status_code == 200
    assert 'x-refreshed-access-token' not in set(r.headers.keys())

    r = client.get('/auth', headers={'Authorization': at})
    assert r.status_code == 200
    assert 'x-refreshed-access-token' not in set(r.headers.keys())


def test_tester(client):
    r = client.post('/login?scopes=tester')
    assert r.status_code == 200

    r = client.get('/tester')
    assert r.status_code == 200
    assert 'x-refreshed-access-token' in set(r.headers.keys())
    at = r.headers.get('x-refreshed-access-token')

    r = client.get('/admin', headers={'Authorization': at})
    assert r.status_code == 403
    assert 'x-refreshed-access-token' not in set(r.headers.keys())

    r = client.get('/auth', headers={'Authorization': at})
    assert r.status_code == 200
    assert 'x-refreshed-access-token' not in set(r.headers.keys())

    r = client.get('/api', headers={'Authorization': at})
    assert r.status_code == 403
    assert 'x-refreshed-access-token' not in set(r.headers.keys())


def test_api(client):
    r = client.post('/login?scopes=api')
    assert r.status_code == 200

    r = client.get('/public')
    assert r.status_code == 200
    assert 'x-refreshed-access-token' in set(r.headers.keys())
    at = r.headers.get('x-refreshed-access-token')

    r = client.get('/admin', headers={'Authorization': at})
    assert r.status_code == 403
    assert 'x-refreshed-access-token' not in set(r.headers.keys())

    r = client.get('/auth', headers={'Authorization': at})
    assert r.status_code == 403
    assert 'x-refreshed-access-token' not in set(r.headers.keys())

    r = client.get('/api', headers={'Authorization': at})
    assert r.status_code == 200
    assert 'x-refreshed-access-token' not in set(r.headers.keys())

    r = client.get('/tester', headers={'Authorization': at})
    assert r.status_code == 403
    assert 'x-refreshed-access-token' not in set(r.headers.keys())
