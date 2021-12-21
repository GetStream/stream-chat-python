from typing import Dict


class StreamResponse(Dict):
    pass


"""
Ideally, this would look something like this:

class StreamResponse(TypedDict, allow_extra=True):
    duration: str

The problem is that Python is not as smart as TypeScript today. `allow_extra` flag
doesn't exist, only `total=False` which is a bit different.

We'll just inherit from Dict until they solve this problem.

https://github.com/python/mypy/issues/4617
"""
