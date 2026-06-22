# MSAR - Security framework
> A comprehensive security framework for FastAPI featuring JWT authentication and authorization, adaptive rate limiting, IP intelligence, and request observation

MSAR is a modular security layer for FastAPI applications. It started as a multi-session JWT auth manager and has evolved into a complete security toolkit for protecting APIs

## Features

### Authentication / Authorization

- 🔐 JWT Access & Refresh token authentication / authorization
- 👥 Multi-session support
- ♻️ Access token rotation
- 🛡️ Scopes support

### Security ( Planned )

- 🌍 IP geolocation lookup
- 🚨 Suspicious activity detection
- 📊 Request observation
- 📝 Content observation
- 🔒 Automatic threat mitigation

### Adaptive Rate Limiting ( Planned )

Unlike traditional rate limiters with fixed request costs, MSAR automatically adjusts endpoint weights based on their computational complexity

Features include:

- ⚖️ Dynamic request weights
- 📈 Automatic endpoint profiling
- 🧠 Adaptive weighting algorithms
- ⚙️ Configurable algorithms
- 🗄️ External Redis storage support

---

## Installation

```bash
pip install msar
```

---

## Quick Start

```python
from fastapi import FastAPI
from msar import AuthManager

app = FastAPI()
am = AuthManager("your-secret-key")
```

Protect routes:

```python
from msar.tokens import AccessToken
from msar import AuthRequired

@app.post("/login")
@am.login
async def login(data):
    user = db.fetch_user(data.email)

    return {'id': user_id}

@app.get("/greet")
@am.auth_manager()
async def greet(access_token: AccessToken):
    name = access_token.get('username')

    return f'Hello, {name}!'

@am.rotation_manager
def rm(request, refresh_token, refresh_manager):
    user_id = refresh_token.get('id')
    user = db.fetch_user(user_id)

    return {'username': user.username}, refresh_manager.build({'id': user_id}).seserialize()
```
