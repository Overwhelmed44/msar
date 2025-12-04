from fastapi import Response

from .policies import CookiePolicy


class Cookie:
    def __init__(self, policy: CookiePolicy, response: Response):
        self.policy = policy
        self.response = response
    
    def set_cookie(self, value: str):
        ...


class RefreshTokenCookie(Cookie):
    def __init__(self, policy: CookiePolicy, response: Response):
        super().__init__(policy, response)
    
    def set_cookie(self, value):
        self.response.set_cookie('refresh_token', value, **self.policy)  # type: ignore


class CookieFactory:
    def __init__(self, cls: type[Cookie], policy: CookiePolicy):
        self.policy = policy
        self.cls = cls
    
    def create(self, response: Response) -> Cookie:
        return self.cls(self.policy, response)
