from typing import Callable, Iterable, Any, Literal
from secrets import token_bytes
from fastapi import Request

from .tokens.token_manager import AccessTokenManager, RefreshTokenManager
from .tokens.policies import AccessTokenPolicy, RefreshTokenPolicy
from .route_managers.rotation_manager import RotationManager
from .route_managers.route_manager import RouteAuthManager
from .route_managers.login_manager import LoginManager
from .tokens.tokens import TokenFactory, AccessToken, RefreshToken
from .cookies.cookies import RefreshTokenCookie
from .cookies.policies import CookiePolicy
from .scopes.use import GlobalScopes
from .scopes.scopes import Scope
from .plugins.plugin_manager import PluginManager

from .abs import ABSAuthManager


class AuthManager(ABSAuthManager):
    '''Provides wrappers and token managers for auth handling'''
    
    def with_(
        self,
        access_token_policy: AccessTokenPolicy | str | bytes | None = None,
        refresh_token_policy: RefreshTokenPolicy | str | bytes | None = None,
        cookie_policy: CookiePolicy | str | None = None,
        scopes: Iterable[Scope] | None = None, 
    ):
        if access_token_policy is None:
            access_token_policy = self.__access_token_policy
        if refresh_token_policy is None:
            refresh_token_policy = self.__refresh_token_policy
        if cookie_policy is None:
            cookie_policy = self.__cookie_policy
        if scopes is None:
            scopes = self.__scopes

        return AuthManager(refresh_token_policy, cookie_policy, scopes, self.pm, access_token_policy=access_token_policy, mode=self.mode)
    
    def auth_manager(self, scopes: Iterable[str] | None = None):
        '''Main wrapper'''

        if scopes is None:
            scopes = set()

        def wrapper(route_handler: Callable):
            route_mgr = RouteAuthManager(self, route_handler, scopes)
            
            return route_mgr.wrapper_factory()
        
        return wrapper
        
    def rotation_manager(self, rotation_handler: Callable):
        '''Wrapper for rotation handler specification. Should not be a FastAPI route handler'''

        self.token_rotator_ = self.token_rotator_.assign_handler(rotation_handler)

        return rotation_handler
    
    def login(self, login_handler: Callable):
        '''Wrapper for handling login. Works just as auth_manager, but does not require tokens on request, only sets them'''

        login_mgr = LoginManager(login_handler, self)

        return login_mgr.get_wrapped()
    
    def signup(self, signup_handler: Callable):
        '''Wrapper for handling signup. Works just as auth_manager, but does not require tokens on request, only sets them'''

        signup_mgr = LoginManager(signup_handler, self)  # same logic as login, so reusing

        return signup_mgr.get_wrapped()

    def use_access(self, jwt_or_payload: str | dict[str, Any]):
        return self.access_f.create(jwt_or_payload)
    
    def use_refresh(self, jwt_or_payload: str | dict[str, Any]):
        return self.refresh_f.create(jwt_or_payload)

    @property
    def cookie_policy(self) -> CookiePolicy:
        return self.__cookie_policy
