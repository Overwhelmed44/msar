from msar.tokens import AccessToken
from .setup import app, am


@app.post("/login")
@am.login
async def login():
    refresh_token = {'scopes': ['auth']}

    return refresh_token


@app.get("/greet")
@am.auth_manager()
async def greet(access_token: AccessToken):
    name = 'msar'

    return f'Hello, {name}!'


@am.rotation_manager
def rm(request, refresh_token, refresh_manager):
    return {'scopes': refresh_token.get('scopes')}, refresh_manager.build({'scopes': ['auth']}).serialize()
