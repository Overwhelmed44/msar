from typing import TypedDict, Literal


class TokenPolicy(TypedDict):
    secret: bytes
    algorithm: str


class AccessTokenPolicy(TokenPolicy):
    ...


class RefreshTokenPolicy(TokenPolicy):
    ...
