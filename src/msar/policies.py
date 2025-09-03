from typing import TypedDict, Literal


class TokenPolicy(TypedDict):
    secret: bytes
    algorithm: str


class AccessTokenPolicy(TokenPolicy):
    ...


class RefreshTokenPolicy(TokenPolicy):
    ...


class CookiePolicy(TypedDict, total=False):
    path: str
    domain: str
    secure: bool
    httponly: bool
    samesite: Literal['lax', 'strict', 'none']


class RefreshTokenCookiePolicy(CookiePolicy):
    ...
