from typing import Iterable
from enum import Enum


class HookAt(Enum):
    BEFORE_REQUEST = 1
    AFTER_REQUEST = 2


class Plugin:
    def __init__(self, hook_at: Iterable[HookAt]):
        self.hook_at = hook_at
