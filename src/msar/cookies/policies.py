from typing import TypedDict, Literal


class CookiePolicy(TypedDict, total=False):
    max_age: int
    path: str
    domain: str
    secure: bool
    httponly: bool
    samesite: Literal['lax', 'strict', 'none']


class RefreshTokenCookiePolicy(CookiePolicy):
    ...
