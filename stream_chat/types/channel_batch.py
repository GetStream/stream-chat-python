import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

ChannelBatchOperation = Literal[
    "addMembers",
    "removeMembers",
    "inviteMembers",
    "assignRoles",
    "addModerators",
    "demoteModerators",
    "hide",
    "show",
    "archive",
    "unarchive",
    "updateData",
    "addFilterTags",
    "removeFilterTags",
]


class ChannelBatchMemberRequest(TypedDict, total=False):
    """
    Represents a member in batch operations.

    Parameters:
        user_id: The ID of the user.
        channel_role: The role of the user in the channel (optional).
    """

    user_id: str
    channel_role: Optional[str]


class ChannelDataUpdate(TypedDict, total=False):
    """
    Represents data that can be updated on channels in batch.

    Parameters:
        frozen: Whether the channel is frozen.
        disabled: Whether the channel is disabled.
        custom: Custom data for the channel.
        team: The team ID for the channel.
        config_overrides: Configuration overrides for the channel.
        auto_translation_enabled: Whether auto-translation is enabled.
        auto_translation_language: The language for auto-translation.
    """

    frozen: Optional[bool]
    disabled: Optional[bool]
    custom: Optional[Dict[str, Any]]
    team: Optional[str]
    config_overrides: Optional[Dict[str, Any]]
    auto_translation_enabled: Optional[bool]
    auto_translation_language: Optional[str]


class ChannelsBatchFilters(TypedDict, total=False):
    """
    Represents filters for batch channel updates.

    Parameters:
        cids: Filter by channel CIDs (can be a dict with operators like $in).
        types: Filter by channel types (can be a dict with operators like $in).
        filter_tags: Filter by filter tags (can be a dict with operators like $in).
    """

    cids: Optional[Any]
    types: Optional[Any]
    filter_tags: Optional[Any]


class ChannelsBatchOptions(TypedDict, total=False):
    """
    Represents options for batch channel updates.

    Parameters:
        operation: The batch operation to perform (required).
        filter: The filter to match channels (required).
        members: List of members for member-related operations (optional).
        data: Channel data updates for updateData operation (optional).
        filter_tags_update: List of filter tags for filter tag operations (optional).
    """

    operation: ChannelBatchOperation
    filter: ChannelsBatchFilters
    members: Optional[List[ChannelBatchMemberRequest]]
    data: Optional[ChannelDataUpdate]
    filter_tags_update: Optional[List[str]]
