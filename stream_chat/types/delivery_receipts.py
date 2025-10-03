import sys
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class DeliveredMessageConfirmation(TypedDict):
    """
    Confirmation of a delivered message.

    Parameters:
        cid: Channel CID (channel_type:channel_id)
        id: Message ID
    """

    cid: str
    id: str


class MarkDeliveredOptions(TypedDict, total=False):
    """
    Options for marking messages as delivered.

    Parameters:
        latest_delivered_messages: List of delivered message confirmations
        user: Optional user object
        user_id: Optional user ID
    """

    latest_delivered_messages: List[DeliveredMessageConfirmation]
    user: Optional[Dict]  # UserResponse equivalent
    user_id: Optional[str]


class ChannelReadStatus(TypedDict, total=False):
    """
    Channel read status information.

    Parameters:
        last_read: Last read timestamp
        unread_messages: Number of unread messages
        user: User information
        first_unread_message_id: ID of first unread message
        last_read_message_id: ID of last read message
        last_delivered_at: Last delivered timestamp
        last_delivered_message_id: ID of last delivered message
    """

    last_read: str  # ISO format string for timestamp
    unread_messages: int
    user: Dict  # UserResponse equivalent
    first_unread_message_id: Optional[str]
    last_read_message_id: Optional[str]
    last_delivered_at: Optional[str]  # ISO format string for timestamp
    last_delivered_message_id: Optional[str]
