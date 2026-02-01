import sys
from enum import IntEnum
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class SortOrder(IntEnum):
    """
    Represents the sort order for a query.
    """

    ASC = 1
    DESC = -1


class SortParam(TypedDict, total=False):
    """
    Represents a sort parameter for a query.

    Parameters:
        field: The field to sort by.
        direction: The direction to sort by.
    """

    field: str
    direction: SortOrder


class Pager(TypedDict, total=False):
    """
    Represents the data structure for a pager.

    Parameters:
        limit: The maximum number of items to return.
        next: The next page token.
        prev: The previous page token.
    """

    limit: Optional[int]
    next: Optional[str]
    prev: Optional[str]


class ParsedPredefinedFilterResponse(TypedDict, total=False):
    """
    Represents the parsed/interpolated predefined filter returned in QueryChannels response.

    This is only present when a predefined filter is used in the query.

    Parameters:
        name: The name of the predefined filter that was used.
        filter: The interpolated filter with placeholders replaced by actual values.
        sort: The interpolated sort parameters (optional).
    """

    name: str
    filter: Dict[str, Any]
    sort: Optional[List[SortParam]]
