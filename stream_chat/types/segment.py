from enum import Enum
from typing import Dict, List, Optional, TypedDict

from stream_chat.types.base import Pager, SortParam


class SegmentType(Enum):
    """
    Represents the type of segment.

    Attributes:
        CHANNEL: A segment targeting channels.
        USER: A segment targeting users.
    """

    CHANNEL = "channel"
    USER = "user"


class SegmentData(TypedDict, total=False):
    """
    Represents the data structure for a segment.

    Parameters:
        name: The name of the segment.
        description: A description of the segment.
        filter: A filter to apply to the segment.
    """

    name: Optional[str]
    description: Optional[str]
    filter: Optional[Dict]


class QuerySegmentsOptions(Pager, total=False):
    sort: Optional[List[SortParam]]


class QuerySegmentTargetsOptions(Pager, total=False):
    sort: Optional[List[SortParam]]
