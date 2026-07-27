from typing import TypedDict


class TokenPolicy(TypedDict):
    secret: bytes
    algorithm: str


class AccessTokenPolicy(TokenPolicy):
    ...


class RefreshTokenPolicy(TokenPolicy):
    ...
