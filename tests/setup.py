from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, Request
from jwt import encode, decode

from src.msar import AuthManager
from src.msar.tokens import AccessToken, RefreshToken
from src.msar.scopes import Hierarchy, Basic

app = FastAPI()
manager = AuthManager(
    {'secret': b'abc', 'algorithm': 'HS256'},
    {'secret': b'def', 'algorithm': 'HS256'},
    {'max_age': 60 * 60 * 24 * 14},
    [Hierarchy(['auth', 'admin']), Basic(['tester'])],
    mode='dev'
)
enc_acc = lambda payload: encode(payload, b'abc', 'HS256')
enc_ref = lambda payload: encode(payload, b'def', 'HS256')


@app.get('/auth_admin')
@manager.auth_manager(['auth'])
def auth_admin(request: Request):
    return JSONResponse({'status': 'ok'})


@app.get('/admin_only')
@manager.auth_manager(['admin'])
def admin_only(request: Request, access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/tester_only')
@manager.auth_manager(['tester'])
def tester_only(request: Request, access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/any')
@manager.auth_manager()
def any_(access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/login')
@manager.login
def login(request: Request):
    return {'scopes': ['auth']}, enc_ref({'scopes': ['auth']})


@app.get('/login_built')
@manager.login
def login_built(request: Request):
    resp = Response()
    resp.set_cookie('refresh_token', enc_ref({'key1': 'value1'}))

    return resp


@manager.rotation_manager
def tr(request, refresh):
    try:
        assert isinstance(request, Request)

        d = decode(refresh, b'def', ['HS256'])
    except:
        return None
  
    return d, enc_ref({'key1': 'value1'})
