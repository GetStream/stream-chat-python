from datetime import datetime
from typing import Optional, TypedDict

from stream_chat.types.base import Pager


class QueryDraftsFilter(TypedDict):
    channel_cid: Optional[str]
    parent_id: Optional[str]
    created_at: Optional[datetime]


class QueryDraftsOptions(Pager):
    pass
