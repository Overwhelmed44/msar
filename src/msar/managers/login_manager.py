from fastapi import Response
from makefun import wraps

from ..auth_manager import AuthManager
from .manager import Manager


class LoginManager(Manager):
    def __init__(self, handler, am: AuthManager):
        super().__init__(handler)

        self.am = am
    
    def get_wrapped(self):

        @wraps(self.handler)
        async def wrapped(*args, **kwargs):
            # route processing ( start )

            if self.is_async:
                response = await self.handler(*args, **kwargs)
            else:
                response = self.handler(*args, **kwargs)
        
            # route processing ( end )
            # after route processing ( start )

            if isinstance(response, Response):
                return response
            
            resp = Response()

            if isinstance(response, str):
                self.am.refresh_mgr.set_token(resp, response, '')
            elif isinstance(response, dict):
                self.am.refresh_mgr.set_token(resp, self.am.refresh_mgr.build(response).serialize(), '')

            return resp

            # after route processing ( end )
        
        return wrapped
