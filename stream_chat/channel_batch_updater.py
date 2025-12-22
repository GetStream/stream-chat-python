from typing import Any, Dict, List, Optional, Union

from stream_chat.base.client import StreamChatInterface
from stream_chat.types.stream_response import StreamResponse


class ChannelBatchUpdater:
    """
    ChannelBatchUpdater - A class that provides convenience methods for batch channel operations
    """

    def __init__(self, client: StreamChatInterface):
        self.client = client

    # Member operations

    def add_members(
        self, filter: Dict[str, Any], members: Union[List[str], List[Dict[str, Any]]]
    ) -> StreamResponse:
        """
        addMembers - Add members to channels matching the filter

        :param filter: Filter to select channels
        :param members: Members to add (list of user IDs or list of member dicts with user_id and channel_role)
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "addMembers",
                "filter": filter,
                "members": members,
            }
        )

    def remove_members(self, filter: Dict[str, Any], members: List[str]) -> StreamResponse:
        """
        removeMembers - Remove members from channels matching the filter

        :param filter: Filter to select channels
        :param members: Member IDs to remove
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "removeMembers",
                "filter": filter,
                "members": members,
            }
        )

    def invite_members(
        self, filter: Dict[str, Any], members: Union[List[str], List[Dict[str, Any]]]
    ) -> StreamResponse:
        """
        inviteMembers - Invite members to channels matching the filter

        :param filter: Filter to select channels
        :param members: Members to invite (list of user IDs or list of member dicts with user_id and channel_role)
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "invites",
                "filter": filter,
                "members": members,
            }
        )

    def add_moderators(self, filter: Dict[str, Any], members: List[str]) -> StreamResponse:
        """
        addModerators - Add moderators to channels matching the filter

        :param filter: Filter to select channels
        :param members: Member IDs to promote to moderator
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "addModerators",
                "filter": filter,
                "members": members,
            }
        )

    def demote_moderators(self, filter: Dict[str, Any], members: List[str]) -> StreamResponse:
        """
        demoteModerators - Remove moderator role from members in channels matching the filter

        :param filter: Filter to select channels
        :param members: Member IDs to demote
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "demoteModerators",
                "filter": filter,
                "members": members,
            }
        )

    def assign_roles(
        self, filter: Dict[str, Any], members: List[Dict[str, Any]]
    ) -> StreamResponse:
        """
        assignRoles - Assign roles to members in channels matching the filter

        :param filter: Filter to select channels
        :param members: Members with role assignments (list of dicts with user_id and channel_role)
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "assignRoles",
                "filter": filter,
                "members": members,
            }
        )

    # Visibility operations

    def hide(self, filter: Dict[str, Any]) -> StreamResponse:
        """
        hide - Hide channels matching the filter

        :param filter: Filter to select channels
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "hide",
                "filter": filter,
            }
        )

    def show(self, filter: Dict[str, Any]) -> StreamResponse:
        """
        show - Show channels matching the filter

        :param filter: Filter to select channels
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "show",
                "filter": filter,
            }
        )

    def archive(self, filter: Dict[str, Any]) -> StreamResponse:
        """
        archive - Archive channels matching the filter

        :param filter: Filter to select channels
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "archive",
                "filter": filter,
            }
        )

    def unarchive(self, filter: Dict[str, Any]) -> StreamResponse:
        """
        unarchive - Unarchive channels matching the filter

        :param filter: Filter to select channels
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "unarchive",
                "filter": filter,
            }
        )

    # Data operations

    def update_data(
        self, filter: Dict[str, Any], data: Dict[str, Any]
    ) -> StreamResponse:
        """
        updateData - Update data on channels matching the filter

        :param filter: Filter to select channels
        :param data: Data to update (frozen, disabled, custom, team, config_overrides, auto_translation_enabled, auto_translation_language)
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "updateData",
                "filter": filter,
                "data": data,
            }
        )

    def add_filter_tags(self, filter: Dict[str, Any], tags: List[str]) -> StreamResponse:
        """
        addFilterTags - Add filter tags to channels matching the filter

        :param filter: Filter to select channels
        :param tags: Tags to add
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "addFilterTags",
                "filter": filter,
                "filter_tags_update": tags,
            }
        )

    def remove_filter_tags(
        self, filter: Dict[str, Any], tags: List[str]
    ) -> StreamResponse:
        """
        removeFilterTags - Remove filter tags from channels matching the filter

        :param filter: Filter to select channels
        :param tags: Tags to remove
        :return: The server response
        """
        return self.client.update_channels_batch(
            {
                "operation": "removeFilterTags",
                "filter": filter,
                "filter_tags_update": tags,
            }
        )

