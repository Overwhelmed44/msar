from fastapi import FastAPI
from msar import AuthManager

app = FastAPI()
am = AuthManager("your-secret-key", {'secure': False}, mode='dev', refresh_token_policy='abc')
enc_acc = lambda p: am.use_access(p).serialize()
enc_ref = lambda p: am.use_refresh(p).serialize()

from . import routes
