from fastapi.responses import JSONResponse
from fastapi import Request, Response
from jwt import decode

from src.msar.tokens import AccessToken, RefreshToken
from .setup import app, manager, enc_ref


@app.get('/auth')
@manager.auth_manager(['auth'])
def auth_admin(request: Request):
    return JSONResponse({'status': 'ok'})


@app.get('/admin')
@manager.auth_manager(['admin'])
def admin_only(request: Request, access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/tester')
@manager.auth_manager(['tester'])
def tester_only(request: Request, access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/api')
@manager.auth_manager(['tester'])
def api(request: Request, access: AccessToken):
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