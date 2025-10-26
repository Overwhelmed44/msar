from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, Request
from jwt import encode, decode

from src.msar import AuthManager, AccessToken

app = FastAPI()
manager = AuthManager(
    {'secret': b'abc', 'algorithm': 'HS256'},
    {'secret': b'def', 'algorithm': 'HS256'},
    {},
    mode='dev'
)
enc_acc = lambda payload: encode(payload, b'abc', 'HS256')
enc_ref = lambda payload: encode(payload, b'def', 'HS256')


@app.get('/req')
@manager.auth_manager(True)
def req(request: Request, access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/not_req')
@manager.auth_manager(False)
def nreq(access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/login')
@manager.login
def login(request: Request):
    return {'key': 'value'}, enc_ref({'key1': 'value1'})


@app.get('/login_built')
@manager.login
def login_built(request: Request):
    resp = Response()
    resp.set_cookie('refresh_token', enc_ref({'key1': 'value1'}))

    return resp


@manager.rotation_manager
def tr(refresh):
    
    try:
        decode(refresh, b'def', ['HS256'])
    except:
        return None
  
    return {'key': 'value'}, enc_ref({'key1': 'value1'})
