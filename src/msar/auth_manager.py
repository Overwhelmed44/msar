from fastapi import Request, Response
from inspect import Parameter
from makefun import wraps
from typing import Callable

from .inspecting_utils import get_request_name, get_access_name, is_async
from .token_manager import TokenManager
from .token_rotator import TokenRotator


class AuthManager:
    def __init__(self, access_manager: TokenManager, refresh_manager: TokenManager):
        self.access_mgr = access_manager
        self.refresh_mgr = refresh_manager

        self.token_rotator_: TokenRotator | None = None
    
    def auth_manager(self, route_handler: Callable):
        route_mgr = RouteAuthManager(route_handler, self)
        
        return route_mgr.wrapper_factory()
    
    def token_rotator(self, rotation_handler: Callable):
        self.token_rotator_ = TokenRotator(rotation_handler)

        return rotation_handler


class RouteAuthManager:
    def __init__(self, func, am: AuthManager):
        self.func = func
        self.is_async = is_async(func)
        self.request_name = get_request_name(func)
        self.access_name = get_access_name(func)

        self.am = am
    
    async def auth_manager_logic(self, func, request_: Request, *args, **kwargs):
        assert self.am.token_rotator_, "Rotate meneger is not present"

        # before route processing ( start )

        access_token = self.am.access_mgr.get(request_)
        if access_token:
            access_token = self.am.access_mgr.resolve(access_token)
        refresh_token = None
        
        if not access_token:
            refresh_token = self.am.refresh_mgr.get(request_)
        
            if not refresh_token:
                return Response(status_code=401)
            
            refreshed = await self.am.token_rotator_.rotate(refresh_token)  # type: ignore

            if not refreshed:
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
            self.am.access_mgr.set(
                response,
                self.am.access_mgr.serialize(access_token)  # type: ignore
            )
            self.am.refresh_mgr.set(response, refresh_token)

        # after route processing ( end )

        return response
    
    def wrapper_factory(self):
        remove_args = []

        if self.access_name:
            remove_args.append(self.access_name)

        @wraps(self.func, remove_args=remove_args)
        async def wrapped_req_passed(*args, **kwargs):
            return await self.auth_manager_logic(self.func, kwargs[self.request_name], *args, **kwargs) # type: ignore
        
        @wraps(self.func, append_args=[Parameter('request', Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)], remove_args=remove_args)
        async def wrapped_req_requested(request: Request, *args, **kwargs):
            return await self.auth_manager_logic(self.func, request, *args, **kwargs)

        if self.request_name:
            return wrapped_req_passed        
        return wrapped_req_requested
