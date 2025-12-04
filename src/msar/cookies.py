from fastapi import Response

from .policies import CookiePolicy


class Cookie:
    policy = None

    def __init__(self, response: Response):
        self.response = response
    
    def set_cookie(self, value: str):
        ...
    
    @classmethod
    def configure(cls, policy: CookiePolicy):
        cls.policy = policy


class RefreshTokenCookie(Cookie):
    def __init__(self, response: Response):
        super().__init__(response)
    
    def set_cookie(self, value):
        self.response.set_cookie('refresh_token', value, **self.__class__.policy)  # type: ignore
