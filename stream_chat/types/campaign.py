import sys
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from stream_chat.types.base import Pager


class MessageTemplate(TypedDict, total=False):
    """
    Represents the data structure for a message template.

    Parameters:
        text: The text of the message.
        attachments: List of the message attachments.
        custom: Custom data.
    """

    text: str
    attachments: Optional[List[Dict]]
    custom: Optional[Dict]


class ChannelTemplate(TypedDict, total=False):
    """
    Represents the data structure for a channel template.

    Parameters:
        type: The type of channel.
        id: The ID of the channel.
        members: List of member IDs.
        custom: Custom data.
    """

    type: str
    id: Optional[str]
    members: Optional[List[str]]
    custom: Optional[Dict]


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
        skip_webhook: Flag to indicate if webhooks should be skipped.
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
    skip_webhook: Optional[bool]


class QueryCampaignsOptions(Pager, total=False):
    pass
