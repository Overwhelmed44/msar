from fastapi import Query

from msar.tokens import AccessToken
from .setup import app, am


@app.post("/login")
@am.login
async def login(scopes: list[str] = Query(None)):
    refresh_token = {'scopes': scopes if scopes else ['auth']}

    return refresh_token


@app.get("/auth")
@am.auth_manager(['auth'])
async def auth(access_token: AccessToken):
    name = 'msar'

    return f'Hello, {name}!'


@app.get("/buggy")
@am.auth_manager(['auth'])
async def buggy(access_token: AccessToken):
    name = 'msar'

    raise Exception()

    return f'Hello, {name}!'


@am.rotation_manager
def rm(request, refresh_token, refresh_manager):
    return {'scopes': refresh_token.get('scopes')}, refresh_manager.build({'scopes': ['auth']}).serialize()
