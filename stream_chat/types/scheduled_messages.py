import datetime
import sys
from typing import List, Union

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict


ScheduledMessageStatus = Literal["scheduled", "sending", "failed", "canceled", "sent"]
"""
Status of a scheduled message. ``canceled`` is reported when a scheduled message
is deleted, ``sent`` only by the ``scheduled_message.sent`` event.
"""


class QueryScheduledMessagesFilter(TypedDict, total=False):
    """
    Narrows a scheduled messages query. Empty fields mean no restriction.

    Parameters:
        cid: Only the scheduled messages of this channel.
        status: Only these statuses: ``scheduled``, ``sending`` and/or ``failed``.
    """

    cid: str
    status: List[ScheduledMessageStatus]


class QueryScheduledMessagesOptions(TypedDict, total=False):
    """
    Pagination of a scheduled messages query.

    Parameters:
        limit: Page size, 1 to 100. Defaults to 20.
        next: The ``next`` value of a previous response, to continue from that point.
    """

    limit: int
    next: str


def format_scheduled_at(scheduled_at: Union[str, datetime.datetime]) -> str:
    """
    Formats a send time for the API. A naive datetime is taken to be in UTC.
    """
    if isinstance(scheduled_at, datetime.datetime):
        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=datetime.timezone.utc)
        return scheduled_at.astimezone(datetime.timezone.utc).isoformat()
    return scheduled_at
