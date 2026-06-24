from fastapi import FastAPI

from msar.scopes import Basic, Hierarchy, Admin
from msar import AuthManager

app = FastAPI()
am = AuthManager(
    "abc",
    {'secure': False},
    [Basic(["api"]), Hierarchy(["tester", "auth"]), Admin(["admin"])],
    mode='dev'
)
enc_acc = lambda p: am.use_access(p).serialize()
enc_ref = lambda p: am.use_refresh(p).serialize()

from . import routes
