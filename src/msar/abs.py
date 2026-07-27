from typing import Callable, Iterable, Any, Literal, Self
from secrets import token_bytes
from fastapi import Request
import logging

from .tokens.token_manager import Token, AccessTokenManager, RefreshTokenManager
from .tokens.policies import AccessTokenPolicy, RefreshTokenPolicy
from .route_managers.rotation_manager import RotationManager
from .tokens.tokens import TokenFactory, AccessToken, RefreshToken
from .cookies.cookies import RefreshTokenCookie
from .cookies.policies import CookiePolicy
from .scopes.use import GlobalScopes
from .scopes.scopes import Scope
from .plugins.plugin_manager import PluginManager
from .safex.safex import Safex


class ABSAuthManager():
    '''Provides wrappers and token managers for auth handling'''

    def __init__(
        self,
        refresh_token_policy: RefreshTokenPolicy | str | bytes | None = None,
        cookie_policy: CookiePolicy | str | None = None,
        scopes: Iterable[Scope] | None = None, 
        plugins: PluginManager | None = None,
        *,
        access_token_policy: AccessTokenPolicy | str | bytes | None = None,
        access_token_manager: type[AccessTokenManager] = AccessTokenManager,
        refresh_token_manager: type[RefreshTokenManager] = RefreshTokenManager,
        mode: Literal['dev', 'prod'] = 'prod'
    ):
        # Defaults
        if access_token_policy is None:
            access_token_policy = token_bytes(32)
        if isinstance(access_token_policy, str):
            access_token_policy = access_token_policy.encode()
        if isinstance(access_token_policy, bytes):
            access_token_policy = AccessTokenPolicy(secret=access_token_policy, algorithm='HS256')
        if refresh_token_policy is None:
            refresh_token_policy = ''
        if isinstance(refresh_token_policy, str):
            refresh_token_policy = refresh_token_policy.encode()
        if isinstance(refresh_token_policy, bytes):
            refresh_token_policy = RefreshTokenPolicy(secret=refresh_token_policy, algorithm='HS256')
        if cookie_policy is None:
            cookie_policy = CookiePolicy({'max_age': 14 * 24 * 60 * 60, 'path': '/', 'secure': True, 'httponly': True, 'samesite': 'lax'})
        if isinstance(cookie_policy, str):
            cookie_policy = CookiePolicy({'max_age': 14 * 24 * 60 * 60, 'path': '/', 'domain': cookie_policy, 'secure': True, 'httponly': True, 'samesite': 'lax'})
        if scopes is None:
            scopes = []

        # Raw args for with_ method
        self.__access_token_policy = access_token_policy
        self.__refresh_token_policy = refresh_token_policy
        self.__cookie_policy = cookie_policy
        self.__scopes = scopes

        self.access_f = TokenFactory(AccessToken, access_token_policy)  # type: ignore
        self.refresh_f = TokenFactory(RefreshToken, refresh_token_policy)  # type: ignore
        self.refresh_cookie = RefreshTokenCookie(cookie_policy)
        self.access_mgr = access_token_manager(self.access_f)
        self.refresh_mgr = refresh_token_manager(self.refresh_f, self.refresh_cookie)
        self.scopes = GlobalScopes(scopes)
        self.pm = plugins or PluginManager.get_default_manager()
        self.token_rotator_ = RotationManager(self.access_mgr, self.refresh_mgr)
        self.mode: Literal['dev', 'prod'] = mode

        self.provide_with: list[type] = [Request, AccessToken]

        self.logger = logging.getLogger('msar')
        self.logger.setLevel(logging.DEBUG if self.mode == 'dev' else logging.WARNING)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))
        self.logger.addHandler(handler)

        self.safex = Safex(self.logger)
    
    def with_(
        self,
        access_token_policy: AccessTokenPolicy | str | bytes | None = None,
        refresh_token_policy: RefreshTokenPolicy | str | bytes | None = None,
        cookie_policy: CookiePolicy | str | None = None,
        scopes: Iterable[Scope] | None = None, 
    ) -> Self:
        ...
    
    def auth_manager(self, scopes: Iterable[str] | None = None) -> Callable:
        ...
        
    def rotation_manager(self, rotation_handler: Callable) -> Callable:
        ...
    
    def login(self, login_handler: Callable) -> Callable:
        ...
    
    def signup(self, signup_handler: Callable) -> Callable:
        ...

    def use_access(self, jwt_or_payload: str | dict[str, Any]) -> Token:
        ...
    
    def use_refresh(self, jwt_or_payload: str | dict[str, Any]) -> Token:
        ...

    @property
    def cookie_policy(self) -> CookiePolicy:
        ...
