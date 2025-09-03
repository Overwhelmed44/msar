from fastapi import Request, Response

from .tokens import Token, AccessToken, RefreshToken
from .cookies import Cookie, RefreshTokenCookie


class TokenManager:
    def __init__(self, token: type[Token] | None, cookie: type[Cookie] | None):
        self.token = token
        self.cookie = cookie
        
    def get(self, request: Request) -> str | None:
        ...
    
    def set(self, response: Response, token: str, type: str) -> None:
        ...
    
    def build(self, payload: dict) -> Token:
        if not self.token:
            raise NotImplementedError
        return self.token(payload)

    def resolve(self, token: str) -> Token | None:
        if not self.token:
            raise NotImplementedError
        return self.token(token)


class DefaultAccessTokenManager(TokenManager):
    def __init__(self, token: type[AccessToken], cookie=None):
        super().__init__(token, cookie)
    
    def get(self, request):
        return request.headers.get('Authorization')
    
    def set(self, response, token, type):
        response.headers.append(f'X-{type}-Access-Token', token)


class DefaultRefreshTokenManager(TokenManager):
    def __init__(self, token: type[RefreshToken] | None, cookie: type[RefreshTokenCookie]):
        super().__init__(token, cookie)
    
    def get(self, request) -> str | None:
        return request.cookies.get('refresh_token')
    
    def set(self, response, token, type) -> None:
        self.cookie(response).set_cookie(token)  # type: ignore
    