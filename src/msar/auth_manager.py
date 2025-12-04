from typing import Callable, Literal, Iterable
from logging import getLogger, INFO

from .token_manager import TokenManager, DefaultAccessTokenManager, DefaultRefreshTokenManager
from .policies import AccessTokenPolicy, RefreshTokenPolicy, CookiePolicy
from .managers.rotation_manager import RotationManager
from .tokens import AccessToken, RefreshToken
from .token_manager import TokenManager
from .cookies import RefreshTokenCookie
from .scopes import GlobalScopes, Scope


class AuthManager:
    '''Provides wrappers for auth handling'''

    def __init__(
        self,
        access_token_policy: AccessTokenPolicy,
        refresh_token_policy: RefreshTokenPolicy,
        cookie_policy: CookiePolicy,
        scopes: Iterable[Scope],
        *,
        access_token_manager: type[TokenManager] = DefaultAccessTokenManager,
        refresh_token_manager: type[TokenManager] = DefaultRefreshTokenManager,
        mode: Literal['prod', 'dev'] = 'prod'
    ):
        self.scopes = GlobalScopes(scopes)
        self.access_mgr = access_token_manager(AccessToken, None)
        self.refresh_mgr = refresh_token_manager(RefreshToken, RefreshTokenCookie)
        self.token_rotator_: RotationManager | None = None
        self.mode = mode == 'dev'

        AccessToken.configure(access_token_policy)
        RefreshToken.configure(refresh_token_policy)
        RefreshTokenCookie.configure(cookie_policy)
    
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

    def log(self, message: str):
        '''Used in development mode'''

        if self.mode:
            print(message)
