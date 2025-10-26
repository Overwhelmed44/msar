from fastapi import Request, Response
from inspect import Parameter
from makefun import wraps

from ..inspecting_utils import get_request_name, get_access_name
from ..auth_manager import AuthManager
from .manager import Manager

class RouteAuthManager(Manager):
    def __init__(self, handler, am: AuthManager, login_required: bool):
        super().__init__(handler)

        self.request_name = get_request_name(handler)
        self.access_name = get_access_name(handler)
        self.am = am
        self.required = login_required
    
    async def auth_manager_logic(self, func, request_: Request, *args, **kwargs):
        assert self.am.token_rotator_, "Rotate manager is not present"

        # before route processing ( start )

        access_token = self.am.access_mgr.get(request_)
        if access_token:
            access_token = self.am.access_mgr.resolve(access_token)
        else:
            self.am.log('(Not required) No access token provided')
        refresh_token = None
        
        if not access_token:
            self.am.log('(Not required) Rotating')
            
            refresh_token = self.am.refresh_mgr.get(request_)

            refreshed = ({}, '-')
            if refresh_token:
                refreshed = await self.am.token_rotator_.rotate(refresh_token)  # type: ignore

                if not refreshed:
                    self.am.log('(Not required) Rotation failed')

                    refreshed = ({}, '-')
            else:
                self.am.log('(Not required) No refresh token provided')
                
            access_token = self.am.access_mgr.build(refreshed[0])
            refresh_token = refreshed[1]

        # before route processing ( end )
        # route processing ( start )

        if self.access_name:
            kwargs[self.access_name] = access_token

        if self.is_async:
            response = await func(*args, **kwargs)
        else:
            response = func(*args, **kwargs)

        assert isinstance(response, Response), 'Form a response inside your route when using auth_manager'

        # route processing ( end )
        # after route processing ( start )

        if refresh_token:
            self.am.log('(Not required) Updating tokens')

            self.am.access_mgr.set(
                    response,
                    access_token.serialize() if access_token else '',
                    'Refreshed'
                )
            self.am.refresh_mgr.set(response, refresh_token, '')

        # after route processing ( end )

        return response
    
    async def required_auth_manager_logic(self, func, request_: Request, *args, **kwargs):
        assert self.am.token_rotator_, "Rotate manager is not present"

        # before route processing ( start )

        access_token = self.am.access_mgr.get(request_)
        if access_token:
            access_token = self.am.access_mgr.resolve(access_token)
        else:
            self.am.log('(Required) No access token provided')
        refresh_token = None
        
        if not access_token:
            self.am.log('(Required) Rotating')

            refresh_token = self.am.refresh_mgr.get(request_)
        
            if not refresh_token:
                self.am.log('(Required) No refresh token provided: 401')

                return Response(status_code=401)

            refreshed = await self.am.token_rotator_.rotate(refresh_token)  # type: ignore

            if not refreshed:
                self.am.log('(Required) Rotation failed: 401')

                return Response(status_code=401)
            
            access_token = self.am.access_mgr.build(refreshed[0])
            refresh_token = refreshed[1]

        # before route processing ( end )
        # route processing ( start )

        if self.access_name:
            kwargs[self.access_name] = access_token

        if self.is_async:
            response = await func(*args, **kwargs)
        else:
            response = func(*args, **kwargs)

        assert isinstance(response, Response), 'Form a response inside your route when using auth_manager'

        # route processing ( end )
        # after route processing ( start )

        if refresh_token:
            self.am.log('(Required) Updating tokens')

            self.am.access_mgr.set(
                    response,
                    access_token.serialize() if access_token else '',
                    'Refreshed'
                )
            self.am.refresh_mgr.set(response, refresh_token, '')

        # after route processing ( end )

        return response
    
    def wrapper_factory(self):
        remove_args = []

        if self.access_name:
            remove_args.append(self.access_name)

        if self.request_name:
            @wraps(self.handler, remove_args=remove_args)
            async def wrapped_req_passed(*args, **kwargs):
                if self.required:
                    return await self.required_auth_manager_logic(self.handler, kwargs[self.request_name], *args, **kwargs)  # type: ignore
                return await self.auth_manager_logic(self.handler, kwargs[self.request_name], *args, **kwargs)  # type: ignore
            
            return wrapped_req_passed
        
        @wraps(self.handler, append_args=[Parameter('request', Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)], remove_args=remove_args)
        async def wrapped_req_requested(request: Request, *args, **kwargs):
            if self.required:
                return await self.required_auth_manager_logic(self.handler, request, *args, **kwargs)
            return await self.auth_manager_logic(self.handler, request, *args, **kwargs)
     
        return wrapped_req_requested
