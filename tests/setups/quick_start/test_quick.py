from fastapi.testclient import TestClient
import pytest

from .setup import app, enc_acc, enc_ref


@pytest.fixture
def client():
    return TestClient(app)


def test_public(client):
    r1 = client.get('/greet')
        
    assert r1.status_code == 200


def test_cycle(client):
    r = client.post('/login')
    assert r.status_code == 200

    r = client.get('/greet')
    assert r.status_code == 200
    assert 'x-refreshed-access-token' in set(r.headers.keys())
    at = r.headers.get('x-refreshed-access-token')

    r = client.get('/greet', headers={'Authorization': at})
    assert r.status_code == 200
    assert 'x-refreshed-access-token' not in set(r.headers.keys())
