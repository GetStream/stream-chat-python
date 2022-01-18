import asyncio
import time
from typing import Any, Awaitable, Callable


def wait_for(condition: Callable[[], Any], timeout: int = 5):
    start = time.time()

    while True:
        if timeout < (time.time() - start):
            raise Exception("Timeout")

        try:
            if condition():
                break
        except Exception:
            pass

        time.sleep(1)


async def wait_for_async(
    condition: Callable[..., Awaitable[Any]], timeout: int = 5, **kwargs
):
    start = time.time()

    while True:
        if timeout < (time.time() - start):
            raise Exception("Timeout")

        try:
            if await condition(**kwargs):
                break
        except Exception:
            pass

        await asyncio.sleep(1)
