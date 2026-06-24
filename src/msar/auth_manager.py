from typing import Callable, Iterable, Any, Literal
from secrets import token_bytes
from fastapi import Request

from .tokens.token_manager import TokenManager, DefaultAccessTokenManager, DefaultRefreshTokenManager
from .policies import AccessTokenPolicy, RefreshTokenPolicy, CookiePolicy
from .managers.rotation_manager import RotationManager
from .tokens.tokens import TokenFactory, AccessToken, RefreshToken
from .tokens.token_manager import TokenManager
from .cookies import CookieFactory, RefreshTokenCookie
from .scopes.use import GlobalScopes
from .scopes.scopes import Scope
from .plugins.plugin_manager import PluginManager


class AuthManager:
    '''Provides wrappers and token managers for auth handling'''

    def __init__(
        self,
        refresh_token_policy: RefreshTokenPolicy | str | bytes | None = None,
        cookie_policy: CookiePolicy | str | None = None,
        scopes: Iterable[Scope] | None = None, 
        plugins: PluginManager | None = None,
        *,
        access_token_policy: AccessTokenPolicy | str | bytes | None = None,
        access_token_manager: type[TokenManager] = DefaultAccessTokenManager,
        refresh_token_manager: type[TokenManager] = DefaultRefreshTokenManager,
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
        self.refresh_cookie_f = CookieFactory(RefreshTokenCookie, cookie_policy)
        self.access_mgr = access_token_manager(self.access_f, None)
        self.refresh_mgr = refresh_token_manager(self.refresh_f, self.refresh_cookie_f)
        self.scopes = GlobalScopes(scopes)
        self.pm = plugins or PluginManager.get_default_manager()
        self.token_rotator_ = RotationManager(self.access_mgr, self.refresh_mgr)
        self.mode: Literal['dev', 'prod'] = mode

        self.provide_with: list[type] = [Request, AccessToken]
    
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
            from .managers.route_manager import RouteAuthManager  # to avoid circular import
            route_mgr = RouteAuthManager(self, route_handler, scopes)
            
            return route_mgr.wrapper_factory()
        
        return wrapper
        
    def rotation_manager(self, rotation_handler: Callable):
        '''Wrapper for rotation handler specification. Should not be a FastAPI route handler'''

        self.token_rotator_ = self.token_rotator_.assign_handler(rotation_handler)

        return rotation_handler
    
    def login(self, login_handler: Callable):
        '''Wrapper for handling login. Works just as auth_manager, but does not require tokens on request, only sets them'''

        from .managers.login_manager import LoginManager  # to avoid circular import
        login_mgr = LoginManager(login_handler, self)

        return login_mgr.get_wrapped()
    
    def signup(self, signup_handler: Callable):
        '''Wrapper for handling signup. Works just as auth_manager, but does not require tokens on request, only sets them'''

        from .managers.login_manager import LoginManager  # to avoid circular import
        signup_mgr = LoginManager(signup_handler, self)  # same logic as login, so reusing

        return signup_mgr.get_wrapped()

    def use_access(self, jwt_or_payload: str | dict[str, Any]):
        return self.access_f.create(jwt_or_payload)
    
    def use_refresh(self, jwt_or_payload: str | dict[str, Any]):
        return self.refresh_f.create(jwt_or_payload)

    @property
    def cookie_policy(self) -> CookiePolicy:
        return self.__cookie_policy

    def log(self, message: str):
        '''Used in development mode'''

        if self.mode == 'dev':
            print(message)
