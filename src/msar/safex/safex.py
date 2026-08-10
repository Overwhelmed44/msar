from inspect import isawaitable
from typing import Callable, Awaitable, TypeVar, ParamSpec, TypeAlias, cast
from logging import Logger

T = TypeVar('T')
V = TypeVar('V')
P = ParamSpec('P')


class Safex:
    def __init__(self, logger: Logger):
        self.__logger = logger

    async def call(self, func: Callable[P, T | Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
        r = func(*args, **kwargs)

        if isawaitable(r):
            return await r

        return r

    async def with_fallback(self, func: Callable[P, T | Awaitable[T]], fb: V, *args: P.args, **kwargs: P.kwargs) -> tuple[None, T] | tuple[Exception, V]:
        try:
            return None, await self.call(func, *args, **kwargs)
        except Exception as exc:
            self.__logger.exception(
                f"Function {func.__name__} failed",
                extra={
                    'fargs': args,
                    "fkwargs": kwargs
                }
            )

            return exc, fb
