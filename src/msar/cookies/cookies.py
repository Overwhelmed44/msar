from fastapi import Request, Response

from .policies import CookiePolicy


class Cookie:
    def __init__(self, name: str, policy: CookiePolicy):
        self.name = name
        self.policy = policy

    def get_cookie(self, request: Request) -> str | None:
        return request.cookies.get(self.name)
    
    def set_cookie(self, response: Response, value: str):
        response.set_cookie(self.name, value, **self.policy)

    def delete_cookie(self, response: Response):
        response.delete_cookie(self.name)


class RefreshTokenCookie(Cookie):
    def __init__(self, policy: CookiePolicy):
        super().__init__('refresh_token', policy)
