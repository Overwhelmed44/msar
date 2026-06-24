from typing import Callable, Coroutine, Any

from msar.tokens.token_manager import TokenManager
from .manager import Manager

type rotation_result_type = tuple[dict, str] | None
type rotation_handler_type = Callable[[str], rotation_result_type | Coroutine[Any, Any, rotation_result_type]]


class RotationManager(Manager):
    def __init__(self, access_m: TokenManager, refresh_m: TokenManager, rotation_handler: rotation_handler_type | None = None):
        if rotation_handler:
            super().__init__(rotation_handler)
        else:
            super().__init__(lambda req, ref: None)
        
        self.access_m = access_m
        self.refresh_m = refresh_m
    
    def assign_handler(self, rotation_handler: rotation_handler_type):
        return RotationManager(self.access_m, self.refresh_m, rotation_handler)
    
    async def rotate(self, request, refresh_token) -> rotation_result_type:
        refresh_is_present = len(self.refresh_m.token.secret) != 0

        if refresh_is_present:
            refresh_token = self.refresh_m.resolve(refresh_token)

            if not refresh_token:
                return None

        args = [request, refresh_token]
        if refresh_is_present:
            args.append(self.refresh_m)

        if self.is_async:
            return await self.handler(*args)  # type: ignore
        return self.handler(*args)  # type: ignore
