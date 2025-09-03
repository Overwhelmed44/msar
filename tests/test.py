from fastapi.testclient import TestClient
from .setup import enc_acc

from jwt import encode


class Tester(TestClient):
    def __init__(self, app):
        super().__init__(app)
    
    def test_valid(self):
        r = self.get('/', cookies={'refresh_token': 'token'})
        self.cookies.clear()

        return r.cookies.get('refresh_token') == 'nekot'

    def test_absent(self):
        r = self.get('/')
        return r.status_code == 401

    def test_access_re(self):
        r = self.get('/', cookies={'refresh_token': 'token'})
        self.cookies.clear()

        return r.headers.get('X-Refreshed-Access-Token') == enc_acc({'key': 'value'})
    
    def test_access_no(self):
        r = self.get('/', headers={'Authentification': enc_acc({'key': 'value'})})

        return r.headers.get('X-Refreshed-Access-Token') is None

    def test_all(self):
        tests = [
            self.test_valid,
            self.test_absent,
            self.test_access_re,
            self.test_access_no
        ]
        
        for test in tests:
            print(test.__name__, test())
