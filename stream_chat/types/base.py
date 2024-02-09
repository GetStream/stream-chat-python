from enum import IntEnum
from typing import TypedDict, Optional, Any


class SortOrder(IntEnum):
    ASC = 1
    DESC = -1


class SortParam(TypedDict, total=False):
    field: str
    direction: SortOrder


class SortField(TypedDict, total=False):
    field: str
    value: Any


class Pager(TypedDict, total=False):
    limit: Optional[int]
    next: Optional[str]
    prev: Optional[str]



