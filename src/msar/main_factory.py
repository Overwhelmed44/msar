from .token_manager import TokenManager, DefaultAccessTokenManager, DefaultRefreshTokenManager
from .auth_manager import AuthManager
from .tokens import AccessToken, RefreshToken
from .cookies import RefreshTokenCookie
from .policies import AccessTokenPolicy, RefreshTokenPolicy, CookiePolicy


class AuthManagerFactory:
    def __init__(
        self,
        access_token_policy: AccessTokenPolicy,
        refresh_token_policy: RefreshTokenPolicy,
        cookie_policy: CookiePolicy,
        *,
        access_token_manager: type[TokenManager] = DefaultAccessTokenManager,
        refresh_token_manager: type[TokenManager] = DefaultRefreshTokenManager
    ):
        self.access_policy = access_token_policy
        self.refresh_policy = refresh_token_policy
        self.cookie_policy = cookie_policy

        self.access_manager = access_token_manager
        self.refresh_manager = refresh_token_manager
    
    def __call__(self):
        AccessToken.configure(self.access_policy)
        RefreshToken.configure(self.refresh_policy)

        RefreshTokenCookie.configure(self.cookie_policy, 60 * 60 * 24 * 14)

        return AuthManager(
            self.access_manager(AccessToken, None),
            self.refresh_manager(RefreshToken, RefreshTokenCookie),
        )
