from typing import overload, Any
from jwt import encode, decode, PyJWTError

from .policies import TokenPolicy


class Token(dict):
    @overload
    def __init__(self, jwt_or_payload: str):
        '''
        For string-encoded jwt
        Decodes jwt into dict with additional methods
        '''
    
    @overload
    def __init__(self, jwt_or_payload: dict[str, Any]):
        '''
        For payload
        Works just as dict but with additional methods
        '''

    def __init__(self, jwt_or_payload: str | dict[str, Any]):
        if isinstance(jwt_or_payload, str):
            super().__init__(self.decode(jwt_or_payload) or {})
        else:
            super().__init__(jwt_or_payload)

    @classmethod
    def configure(cls, token_policy: TokenPolicy) -> None:
        cls.secret = token_policy.get('secret')
        cls.alg = token_policy.get('algorithm')
    
    @classmethod
    def encode(cls, payload: dict):
        return encode(payload, cls.secret, cls.alg)
    
    @classmethod
    def decode(cls, jwt: str, verify_exp: bool = True):
        try:
            return decode(jwt, cls.secret, [cls.alg], options={"verify_exp": verify_exp})
        except PyJWTError:
            return None
    
    def serialize(self) -> str:
        return self.__class__.encode(self)


class AccessToken(Token):
    ...


class RefreshToken(Token):
    ...
