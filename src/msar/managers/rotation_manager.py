from typing import Callable, Coroutine, Any

from .manager import Manager

type rotation_result_type = tuple[dict, str] | None
type rotation_handelr_type = Callable[[str], rotation_result_type | Coroutine[Any, Any, rotation_result_type]]


class RotationManager(Manager):
    def __init__(self, rotation_handler: rotation_handelr_type):
        super().__init__(rotation_handler)
    
    async def rotate(self, refresh_token) -> rotation_result_type:
        if self.is_async:
            return await self.handler(refresh_token)  # type: ignore
        return self.handler(refresh_token)  # type: ignore
