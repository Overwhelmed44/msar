from fastapi import Request, Response

from .tokens import TokenFactory, Token, AccessToken, RefreshToken
from .cookies import Cookie, CookieFactory


class TokenManager:
    def __init__(self, token: TokenFactory | None, cookie: CookieFactory | None):
        self.token = token
        self.cookie = cookie
        
    def get(self, request: Request) -> str | None:
        ...
    
    def set(self, response: Response, token: str, type: str) -> None:
        ...
    
    def build(self, payload: dict) -> Token:
        if not self.token:
            raise NotImplementedError
        return self.token.create(payload)

    def resolve(self, token: str) -> Token | None:
        if not self.token:
            raise NotImplementedError
        return self.token.create(token)


class DefaultAccessTokenManager(TokenManager):
    def __init__(self, token: TokenFactory, cookie=None):
        super().__init__(token, cookie)
    
    def get(self, request):
        return request.headers.get('Authorization')
    
    def set(self, response, token, type):
        if token:
            response.headers.append(f'X-{type}-Access-Token', token)


class DefaultRefreshTokenManager(TokenManager):
    def __init__(self, token: TokenFactory | None, cookie: CookieFactory):
        super().__init__(token, cookie)
    
    def get(self, request) -> str | None:
        return request.cookies.get('refresh_token')
    
    def set(self, response, token, type) -> None:
        if token == '-':
            response.delete_cookie('refresh_token')
        else:
            self.cookie.create(response).set_cookie(token)  # type: ignore
    