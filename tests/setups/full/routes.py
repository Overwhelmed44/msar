from fastapi import Query

from msar.tokens import AccessToken
from .setup import app, am


@app.post("/login")
@am.login
async def login(scopes: list[str] = Query(None)):
    refresh_token = {'scopes': scopes if scopes else ['auth']}

    return refresh_token


@app.get("/public")
@am.auth_manager()
async def public(access_token: AccessToken):
    name = 'msar'

    return f'Hello, {name}!'


@app.get("/api")
@am.auth_manager(['api'])
async def api(access_token: AccessToken):
    name = 'msar'

    return f'Hello, {name}!'


@app.get("/tester")
@am.auth_manager(['tester'])
async def tester(access_token: AccessToken):
    name = 'msar'

    return f'Hello, {name}!'


@app.get("/auth")
@am.auth_manager(['auth'])
async def auth(access_token: AccessToken):
    name = 'msar'

    return f'Hello, {name}!'


@app.get("/admin")
@am.auth_manager(['admin'])
async def admin(access_token: AccessToken):
    name = 'msar'

    return f'Hello, {name}!'


@am.rotation_manager
def rm(request, refresh_token, refresh_manager):
    return {'scopes': refresh_token.get('scopes')}, refresh_manager.build({'scopes': ['auth']}).serialize()
