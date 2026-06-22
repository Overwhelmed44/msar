from fastapi import FastAPI
from jwt import encode, decode

from src.msar import AuthManager
from src.msar.scopes.scopes import Hierarchy, Basic, Admin

app = FastAPI()
manager = AuthManager(
    'abc',
    'def',
    scopes=[Hierarchy(['tester', 'auth']), Basic(['api']), Admin(['admin'])],
    mode='dev'
)
oth = manager.with_(scopes=[Basic(['oth'])])
enc_acc = lambda payload: encode(payload, b'abc', 'HS256')
enc_ref = lambda payload: encode(payload, b'def', 'HS256')

from . import routes 
