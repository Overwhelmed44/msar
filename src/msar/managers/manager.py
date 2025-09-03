from typing import Callable

from ..inspecting_utils import is_async


class Manager:
    '''Base class for managers implemented as wrappers'''

    def __init__(self, handler: Callable):
        self.handler = handler
        self.is_async = is_async(handler)
    