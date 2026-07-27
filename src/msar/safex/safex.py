from inspect import iscoroutinefunction
from typing import Callable, Awaitable, TypeVar, ParamSpec, TypeAlias, cast
from logging import Logger

T = TypeVar('T')
V = TypeVar('V')
P = ParamSpec('P')


class Safex:
    def __init__(self, logger: Logger):
        self.__logger = logger

    async def call(self, func: Callable[P, T | Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
        if iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return cast(T, func(*args, **kwargs))

    async def with_fallback(self, func: Callable[P, T | Awaitable[T]], fb: V, *args: P.args, **kwargs: P.kwargs) -> T | V:
        try:
            return await self.call(func, *args, **kwargs)
        except Exception as ex:
            self.__logger.exception(
                repr(ex),
                extra={
                    'function': func.__name__,
                    'fargs': args,
                    "fkwargs": kwargs
                }
            )

        return fb
