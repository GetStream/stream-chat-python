import datetime
from typing import Dict, List, Optional, TypedDict, Union

from stream_chat.types.base import Pager, SortParam


class MessageTemplate(TypedDict, total=False):
    """
    Represents the data structure for a message template.

    Parameters:
        text: The text of the message.
        attachments: List of the message attachments.
    """

    text: str
    attachments: Optional[List[Dict]]


class ChannelTemplate(TypedDict, total=False):
    """
    Represents the data structure for a channel template.

    Parameters:
        type: The type of channel.
        id: The ID of the channel.
    """

    type: str
    id: str


class CampaignData(TypedDict, total=False):
    """
    Represents the data structure for a campaign.

    Either `segment_ids` or `user_ids` must be provided, but not both.

    If `create_channels` is True, `channel_template` must be provided.

    Parameters:
        message_template: The template for the message to be sent in the campaign.
        sender_id: The ID of the user who is sending the campaign.
        segment_ids: List of segment IDs the campaign is targeting.
        user_ids: List of individual user IDs the campaign is targeting.
        create_channels: Flag to indicate if new channels should be created for the campaign.
        channel_template: The template for channels to be created, if applicable.
        name: The name of the campaign.
        description: A description of the campaign.
        skip_push: Flag to indicate if push notifications should be skipped.
        scheduled_for: The scheduled time for the campaign. Can be a string or a datetime object.
    """

    message_template: MessageTemplate
    sender_id: str
    segment_ids: Optional[List[str]]
    user_ids: Optional[List[str]]
    create_channels: Optional[bool]
    channel_template: Optional[ChannelTemplate]
    name: Optional[str]
    description: Optional[str]
    skip_push: Optional[bool]
    scheduled_for: Optional[Union[str, datetime.datetime]]


class QueryCampaignsOptions(Pager, total=False):
    sort: Optional[List[SortParam]]
