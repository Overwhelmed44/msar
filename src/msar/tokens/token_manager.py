from fastapi import Request, Response

from .tokens import TokenFactory, Token
from msar.cookies.cookies import RefreshTokenCookie


class TokenManager:
    def __init__(self, token: TokenFactory):
        self.token = token
        
    def get_token(self, request: Request) -> str | None:
        ...
    
    def set_token(self, response: Response, token: str) -> None:
        ...
    
    def build(self, payload: dict) -> Token:
        if not self.token:
            raise NotImplementedError
        return self.token.create(payload)

    def resolve(self, token: str) -> Token | None:
        if not self.token:
            raise NotImplementedError
        return self.token.create(token)


class AccessTokenManager(TokenManager):
    def __init__(self, token: TokenFactory):
        super().__init__(token)
    
    def get_token(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return None

        spl = token.split()

        if len(spl) != 2:
            return None
        
        schema, token = spl

        if schema != 'Bearer':
            return None

        return token
    
    def set_token(self, response, token):
        if token:
            response.headers.append(f'X-Access-Token', f'{token}')


class RefreshTokenManager(TokenManager):
    def __init__(self, token: TokenFactory, cookie: RefreshTokenCookie):
        super().__init__(token)

        self.cookie = cookie
    
    def get_token(self, request):
        return self.cookie.get_cookie(request)
    
    def set_token(self, response, token):
        if token == '-':
            self.cookie.delete_cookie(response)
        else:
            self.cookie.set_cookie(response, token)
    