import functools
import asyncio
from collections.abc import Callable, Awaitable
from typing import Protocol

def to_thread_decorator[**P, T](func: Callable[P,T]):
    @functools.wraps(func)
    async def wrapper(*args:P.args, **kwargs:P.kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper

class AsyncCallable[**P, T](Protocol[P, T]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Awaitable[T]: ...