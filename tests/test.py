from fastapi.testclient import TestClient
from inspect import getmembers

from .setup.setup import enc_acc, enc_ref


class Tester(TestClient):
    def __init__(self, app):
        super().__init__(app)
    
    def test_admin(self):
        r1 = self.get('/admin', cookies={'refresh_token': enc_ref({'scopes': ['admin']})})
        self.cookies.clear()

        r2 = self.get('/api', cookies={'refresh_token': enc_ref({'scopes': ['admin']})})
        self.cookies.clear()

        r3 = self.get('/tester', cookies={'refresh_token': enc_ref({'scopes': ['admin']})})
        self.cookies.clear()

        return all((
            r1.cookies.get('refresh_token') == enc_ref({'key1': 'value1'}),
            r2.cookies.get('refresh_token') == enc_ref({'key1': 'value1'}),
            r3.cookies.get('refresh_token') == enc_ref({'key1': 'value1'})
        ))

    def test_auth(self):
        r1 = self.get('/auth', cookies={'refresh_token': enc_ref({'scopes': ['auth']})})
        self.cookies.clear()

        r2 = self.get('/any', cookies={'refresh_token': enc_ref({'scopes': ['auth']})})
        self.cookies.clear()

        r3 = self.get('/api', cookies={'refresh_token': enc_ref({'scopes': ['auth']})})
        self.cookies.clear()

        r4 = self.get('/tester', cookies={'refresh_token': enc_ref({'scopes': ['auth']})})
        self.cookies.clear()


        return all((
            r1.cookies.get('refresh_token') == enc_ref({'key1': 'value1'}),
            r2.cookies.get('refresh_token') == enc_ref({'key1': 'value1'}),
            r3.status_code == 403,
            r4.status_code == 403
        ))
    
    def test_tester(self):
        r1 = self.get('/auth', cookies={'refresh_token': enc_ref({'scopes': ['tester']})})
        self.cookies.clear()

        r2 = self.get('/tester', cookies={'refresh_token': enc_ref({'scopes': ['tester']})})
        self.cookies.clear()


        return all((
            r1.cookies.get('refresh_token') == enc_ref({'key1': 'value1'}),
            r2.cookies.get('refresh_token') == enc_ref({'key1': 'value1'})
        ))
    
    def test_public(self):
        r = self.get('/any')

        return r.status_code == 200
    
    def test_login(self):
        r = self.get('/login')
        self.cookies.clear()

        return bool(r.headers.get('X-Issued-Access-Token')) and bool(r.cookies.get('refresh_token'))
    
    def test_login_built(self):
        r = self.get('/login_built')
        self.cookies.clear()

        return r.cookies.get('refresh_token') == enc_ref({'key1': 'value1'})
    
    def test_cycle(self):
        r = self.get('/login')
        access = r.headers.get('X-Issued-Access-Token')
        refresh = r.cookies.get('refresh_token')
        self.cookies.clear()

        if not access or not refresh:
            return False

        r = self.get('/auth', headers={'Authorization': access})
        if not r.status_code == 200:
            return False
        
        r = self.get('/auth', cookies={'refresh_token': refresh})
        self.cookies.clear()

        return r.headers.get('X-Refreshed-Access-Token') == access
    
    def test_multiple(self):
        r = self.get('/login')
        access = r.headers.get('X-Issued-Access-Token')
        refresh = r.cookies.get('refresh_token') or ''
        self.cookies.clear()

        for _ in range(5):
            r = self.get('/auth', headers={'Authorization': access}, cookies={'refresh_token': refresh})
            
            if not r.status_code == 200 or r.headers.get('X-Refreshed-Access-Token'):
                return False
        
        return True

    def test_all(self):
        tests = [(name.removeprefix('test_'), func) for name, func in getmembers(self) if name.startswith("test_") and name != 'test_all']
        
        passed = 0
        for test_obj in tests:
            result = test_obj[1]()
            passed += result

            print(test_obj[0], ('failed', 'passed')[result])
        print()

        if passed == len(tests):
            print('All tests passed')
        else:
            print(f'{passed}/{len(tests)} tests passed')    
