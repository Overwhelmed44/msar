from typing import Callable, Iterable, Any

from .token_manager import TokenManager, DefaultAccessTokenManager, DefaultRefreshTokenManager
from .policies import AccessTokenPolicy, RefreshTokenPolicy, CookiePolicy
from .managers.rotation_manager import RotationManager
from .tokens import TokenFactory, AccessToken, RefreshToken
from .token_manager import TokenManager
from .cookies import CookieFactory, RefreshTokenCookie
from .scopes import GlobalScopes, Scope


class AuthManager:
    '''Provides wrappers and token managers for auth handling'''

    def __init__(
        self,
        access_token_policy: AccessTokenPolicy,
        refresh_token_policy: RefreshTokenPolicy,
        cookie_policy: CookiePolicy,
        scopes: Iterable[Scope],
        *,
        access_token_manager: type[TokenManager] = DefaultAccessTokenManager,
        refresh_token_manager: type[TokenManager] = DefaultRefreshTokenManager,
        mode: str = 'prod'  # 'prod' | 'dev'
    ):
        # Init args for with_ method
        self.__access_token_policy = access_token_policy
        self.__refresh_token_policy = refresh_token_policy
        self.__cookie_policy = cookie_policy
        self.__scopes = scopes

        self.access_f = TokenFactory(AccessToken, access_token_policy)
        self.refresh_f = TokenFactory(RefreshToken, refresh_token_policy)
        self.refresh_cookie_f = CookieFactory(RefreshTokenCookie, cookie_policy)
        self.access_mgr = access_token_manager(self.access_f, None)
        self.refresh_mgr = refresh_token_manager(self.refresh_f, self.refresh_cookie_f)
        self.scopes = GlobalScopes(scopes)
        self.token_rotator_: RotationManager | None = None
        self.mode = mode
    
    def with_(
        self,
        access_token_policy: AccessTokenPolicy | None = None,
        refresh_token_policy: RefreshTokenPolicy | None = None,
        cookie_policy: CookiePolicy | None = None,
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

        return AuthManager(access_token_policy, refresh_token_policy, cookie_policy, scopes, mode=self.mode)
    
    def auth_manager(self, scopes: Iterable[str] = set()):
        '''Main wrapper'''

        def wrapper(route_handler: Callable):
            from .managers.route_manager import RouteAuthManager  # to avoid circular import
            route_mgr = RouteAuthManager(self, route_handler, scopes)
            
            return route_mgr.wrapper_factory()
        
        return wrapper
        
    def rotation_manager(self, rotation_handler: Callable):
        '''Wrapper for rotation handler specification. Should not be a FastAPI route handler'''

        self.token_rotator_ = RotationManager(rotation_handler)

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
