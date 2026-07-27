from typing import Callable

from .utils.inspecting import is_async


class Manager:
    '''Base class for managers implemented as wrappers'''

    def __init__(self, handler: Callable):
        self.handler = handler
        self.is_async = is_async(handler)
    