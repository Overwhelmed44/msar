from fastapi import Request, Response

from .tokens import TokenFactory, Token, AccessToken, RefreshToken
from msar.cookies import Cookie, CookieFactory


class TokenManager:
    def __init__(self, token: TokenFactory, cookie: CookieFactory | None):
        self.token = token
        self.cookie = cookie
        
    def get_token(self, request: Request) -> str | None:
        ...
    
    def set_token(self, response: Response, token: str, tp: str) -> None:
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
    
    def get_token(self, request):
        return request.headers.get('Authorization')
    
    def set_token(self, response, token, tp):
        if token:
            response.headers.append(f'X-{tp}-Access-Token', token)


class DefaultRefreshTokenManager(TokenManager):
    def __init__(self, token: TokenFactory, cookie: CookieFactory):
        super().__init__(token, cookie)
    
    def get_token(self, request):
        return request.cookies.get('refresh_token')
    
    def set_token(self, response, token, tp):
        if token == '-':
            response.delete_cookie('refresh_token')
        else:
            self.cookie.create(response).set_cookie(token)  # type: ignore
    