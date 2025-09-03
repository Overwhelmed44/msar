from .inspecting_utils import is_async
from typing import Callable, Coroutine, Any

type rotation_result_type = tuple[dict, str] | None
type rotation_handelr_type = Callable[[str], rotation_result_type | Coroutine[Any, Any, rotation_result_type]]


class TokenRotator:
    def __init__(self, rotation_handler: rotation_handelr_type):
        self.rotation_handler = rotation_handler
        self.is_async = is_async(rotation_handler)
    
    async def rotate(self, refresh_token) -> rotation_result_type:
        if self.is_async:
            return await self.rotation_handler(refresh_token)  # type: ignore
        return self.rotation_handler(refresh_token)  # type: ignore
