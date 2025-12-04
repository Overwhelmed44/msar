from typing import overload, Any
from jwt import encode, decode, PyJWTError

from .policies import TokenPolicy


class Token(dict):
    @overload
    def __init__(self, secret: bytes, alg: str, jwt_or_payload: str):
        '''
        For string-encoded jwt
        Decodes jwt into dict with additional methods
        '''
    
    @overload
    def __init__(self, secret: bytes, alg: str, jwt_or_payload: dict[str, Any]):
        '''
        For payload
        Works just as dict but with additional methods
        '''

    def __init__(self, secret: bytes, alg: str, jwt_or_payload: str | dict[str, Any]):
        self.secret = secret
        self.alg = alg

        if isinstance(jwt_or_payload, str):
            super().__init__(self.decode(jwt_or_payload) or {})
        else:
            super().__init__(jwt_or_payload)
    
    def encode(self, payload: dict):
        return encode(payload, self.secret, self.alg)
    
    def decode(self, jwt: str, verify_exp: bool = True):
        try:
            return decode(jwt, self.secret, [self.alg], options={"verify_exp": verify_exp})
        except PyJWTError:
            return None
    
    def serialize(self) -> str:
        return self.encode(self)


class AccessToken(Token):
    ...


class RefreshToken(Token):
    ...


class TokenFactory():
    def __init__(self, cls: type[Token], token_policy: TokenPolicy):
        self.cls = cls
        self.secret = token_policy.get('secret')
        self.alg = token_policy.get('algorithm')
    
    def create(self, jwt_or_payload: str | dict[str, Any]) -> Token:
        return self.cls(self.secret, self.alg, jwt_or_payload)
