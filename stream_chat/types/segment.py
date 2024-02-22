import sys
from enum import Enum
from typing import Dict, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from stream_chat.types.base import Pager


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
    pass


class QuerySegmentTargetsOptions(Pager, total=False):
    pass
