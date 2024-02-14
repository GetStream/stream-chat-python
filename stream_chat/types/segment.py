from enum import Enum
from typing import TypedDict, Optional, Dict, List

from stream_chat.types.base import Pager, SortParam


class SegmentType(Enum):
    CHANNEL = "channel"
    USER = "user"


class SegmentData(TypedDict, total=False):
    name: Optional[str]
    description: Optional[str]
    filter: Optional[Dict]


class QuerySegmentsOptions(Pager, total=False):
    sort: Optional[List[SortParam]]
