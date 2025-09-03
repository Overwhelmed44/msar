from fastapi.responses import JSONResponse
from fastapi import FastAPI
from jwt import encode

from src.msar import AuthManager
from src.msar.tokens import AccessToken

app = FastAPI()
manager = AuthManager({'secret': b'abc', 'algorithm': 'HS256'}, {'secret': b'def', 'algorithm': 'HS256'}, {})()
enc_acc = lambda payload: encode(payload, b'abc', 'HS256')


@app.get('/')
@manager.auth_manager
def root(access: AccessToken):
    return JSONResponse({'status': 'ok'})


@manager.token_rotator
def tr(refresh):
    return {'key': 'value'}, refresh[::-1]
