from functools import wraps
from typing import Callable, Any, Awaitable, Dict, Tuple, Self, TypeVar, Generic

from async_property.base import AsyncPropertyDescriptor
from async_property.cached import AsyncCachedPropertyDescriptor

T = TypeVar("T")

class Fluent(Awaitable[T], Generic[T]):
    def __init__(
        self,
        fn: Callable[..., Awaitable[T]],
        args: Tuple[Any, ...] = None,
        kwargs: Dict[str, Any] = None,
        operation: str = '.start',
    ) -> None:
        self._fn = fn
        self._args = args or tuple()
        self._kwargs = kwargs or dict()
        self._operation = operation

    def __getattr__(self, item) -> Self:
        async def passthrough() -> Any:
            current = await self
            if isinstance(current, Awaitable):
                return getattr(await current, item)
            return getattr(current, item)
        return Fluent(passthrough, operation=f'(await {self._operation}).{item}')

    def __get__(self, instance, owner):
        async def passthrough() -> Any:
            current = await self
            if isinstance(current, Awaitable):
                return (await current).__get__(instance, owner)
            return current.__get__(instance, owner)
        return Fluent(passthrough, operation=self._operation)

    def __set__(self, instance, value):
        async def passthrough() -> Any:
            current = await self
            if isinstance(current, Awaitable):
                return (await current).__set__(instance, value)
            return current.__set__(instance, value)
        return Fluent(passthrough, operation=f'{self._operation} = {value!r}')

    def __delete__(self, instance):
        async def passthrough() -> Any:
            current = await self
            if isinstance(current, Awaitable):
                return (await current).__delete__(instance)
            return current.__delete__(instance)
        return Fluent(passthrough, operation=f'del {self._operation}')

    def __call__(self, *args, **kwargs) -> Self:
        async def passthrough() -> Any:
            current = await self
            result = current(*args, **kwargs)
            if isinstance(result, Awaitable):
                return await result
            return result

        args_passing = ', '.join([*(repr(a) for a in args), *(f'{k}={v!r}' for k, v in kwargs.items())])
        return Fluent(passthrough, operation=f'{self._operation}({args_passing})')

    def __await__(self):
        return self._fn(*(self._args or []), **(self._kwargs or {})).__await__()

    def __repr__(self) -> str:
        args_passing = ', '.join([*(repr(a) for a in self._args), *(f'{k}={v!r}' for k, v in self._kwargs.items())])
        return f'{self._operation}({args_passing})'


def fluent(
    fn: Callable[..., Awaitable[T]] | AsyncPropertyDescriptor | AsyncCachedPropertyDescriptor,
) -> Callable[..., Awaitable[T]]:
    """
    Decorates a method so that it can be used in a fluent manner.

    Calls to this method then can be chained with other async methods, with a single await expression wrapping them all.

    >>> from typing import cast, Self
    >>> from fluent_async import fluent
    >>> import asyncio
    >>>
    >>> class Example:
    ...     def __init__(self):
    ...         self.calls = []
    ...
    ...     @fluent
    ...     async def head(self) -> Self:
    ...         self.calls.append('head')
    ...         return self
    ...
    ...     head = cast(Callable[..., Self], head)
    ...
    ...     async def body(self) -> Self:
    ...         self.calls.append('body')
    ...         return self
    ...
    ...     body = cast(Callable[..., Self], body)
    ...
    ...     @fluent
    ...     async def tail(self) -> Self:
    ...         self.calls.append('tail')
    ...         return self
    ...
    ...     tail = cast(Callable[..., Self], tail)
    ...
    >>> async def main():
    ...     assert ['head', 'body', 'tail'] == await Example().head().body().tail()
    ...
    >>> asyncio.run(main())

    :param fn: async function to be decorated.
    :return: wrapped function.
    """

    if not callable(fn):
        async def passthrough():
            return fn
        return Fluent(passthrough, operation='.' + fn.field_name)

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Awaitable[T]:
        return Fluent(fn, args, kwargs, operation='.' + fn.__name__)

    return wrapper


__all__ = [
    'fluent',
]
