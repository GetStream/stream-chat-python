from typing import List, Optional, TypedDict, Dict

from stream_chat.types.base import Pager, SortParam


class TestData(TypedDict):
    name: str


class MessageTemplate(TypedDict, total=False):
    text: str
    attachments: Optional[List[Dict]]


class CampaignData(TypedDict, total=False):
    message_template: MessageTemplate
    segments: List[str]
    sender_id: str
    description: Optional[str]
    name: Optional[str]


class QueryCampaignsOptions(Pager, total=False):
    sort: Optional[List[SortParam]]





