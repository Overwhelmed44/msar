from fastapi.testclient import TestClient
import pytest

from .setup import app, enc_acc, enc_ref


@pytest.fixture
def client():
    return TestClient(app)


def test_auth_cycle_break_after(client):
    r = client.post('/login')
    assert r.status_code == 200

    r = client.get('/auth')
    assert r.status_code == 200
    assert 'x-access-token' in set(r.headers.keys())
    at = r.headers.get('x-access-token')

    r = client.get('/buggy', headers={'Authorization': f'Bearer {at}'})
    assert r.status_code == 500
    assert 'x-access-token' not in set(r.headers.keys())

    r = client.get('/auth', headers={'Authorization': f'Bearer {at}'})
    assert r.status_code == 200
    assert 'x-access-token' not in set(r.headers.keys())


def test_auth_cycle_break_first(client):
    r = client.post('/login')
    assert r.status_code == 200

    r = client.get('/buggy')
    assert r.status_code == 500
    assert 'x-access-token' in set(r.headers.keys())
    at = r.headers.get('x-access-token')

    r = client.get('/auth', headers={'Authorization': f'Bearer {at}'})
    assert r.status_code == 200
    assert 'x-access-token' not in set(r.headers.keys())
