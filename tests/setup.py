from fastapi.responses import JSONResponse
from fastapi import FastAPI
from jwt import encode, decode

from src.msar import AuthManager, AccessToken

app = FastAPI()
manager = AuthManager(
    {'secret': b'abc', 'algorithm': 'HS256'},
    {'secret': b'def', 'algorithm': 'HS256'},
    {}
)
enc_acc = lambda payload: encode(payload, b'abc', 'HS256')
enc_ref = lambda payload: encode(payload, b'def', 'HS256')


@app.get('/')
@manager.auth_manager
def root(access: AccessToken):
    return JSONResponse({'status': 'ok'})


@app.get('/login')
@manager.login
def login():
    return {'key': 'value'}, enc_ref({'key1': 'value1'})


@manager.rotation_manager
def tr(refresh):
    
    try:
        decode(refresh, b'def', ['HS256'])
    except:
        return None
  
    return {'key': 'value'}, enc_ref({'key1': 'value1'})
