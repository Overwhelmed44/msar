from fastapi.testclient import TestClient
from .setup import enc_acc, enc_ref


class Tester(TestClient):
    def __init__(self, app):
        super().__init__(app)
    
    def test_valid(self):
        r = self.get('/', cookies={'refresh_token': enc_ref({'key': 'value'})})
        self.cookies.clear()

        return r.cookies.get('refresh_token') == enc_ref({'key1': 'value1'})

    def test_absent(self):
        r = self.get('/')
        return r.status_code == 401

    def test_access_re(self):
        r = self.get('/', cookies={'refresh_token': enc_ref({'key': 'value'})})
        self.cookies.clear()

        return r.headers.get('X-Refreshed-Access-Token') == enc_acc({'key': 'value'})
    
    def test_access_no(self):
        r = self.get('/', headers={'Authentification': enc_acc({'key': 'value'})})

        return r.headers.get('X-Refreshed-Access-Token') is None
    
    def test_cycle(self):
        r = self.get('/login')
        access = r.headers.get('X-Issued-Access-Token')
        refresh = r.cookies.get('refresh_token')

        if not access or not refresh:
            return False

        r = self.get('/', headers={'Authorization': access})
        if not r.status_code == 200:
            return False
        
        r = self.get('/', cookies={'refresh_token': enc_ref({'key': 'value'})})
        self.cookies.clear()

        return r.headers.get('X-Refreshed-Access-Token') == enc_acc({'key': 'value'})

    def test_all(self):
        tests = [
            self.test_valid,
            self.test_absent,
            self.test_access_re,
            self.test_access_no,
            self.test_cycle
        ]
        
        passed = 0
        for test in tests:
            result = test()
            passed += result

            print(test.__name__.lstrip('test_'), ('failed', 'passed')[result])
        print()

        if passed == len(tests):
            print('All tests passed')
        else:
            print(f'{passed}/{len(tests)} tests passed')    
