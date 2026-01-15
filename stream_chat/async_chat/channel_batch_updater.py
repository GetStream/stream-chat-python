from typing import TYPE_CHECKING, List

from stream_chat.types.channel_batch import (
    ChannelBatchMemberRequest,
    ChannelDataUpdate,
    ChannelsBatchFilters,
    ChannelsBatchOptions,
)
from stream_chat.types.stream_response import StreamResponse

if TYPE_CHECKING:
    from stream_chat.async_chat.client import StreamChatAsync


class ChannelBatchUpdater:
    """
    Provides convenience methods for batch channel operations (async).
    """

    def __init__(self, client: "StreamChatAsync") -> None:
        self.client = client

    async def add_members(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Adds members to channels matching the filter.

        :param filter: The filter to match channels.
        :param members: List of members to add.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "addMembers",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def remove_members(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Removes members from channels matching the filter.

        :param filter: The filter to match channels.
        :param members: List of members to remove.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "removeMembers",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def invite_members(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Invites members to channels matching the filter.

        :param filter: The filter to match channels.
        :param members: List of members to invite.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "inviteMembers",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def add_moderators(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Adds moderators to channels matching the filter.

        :param filter: The filter to match channels.
        :param members: List of members to add as moderators.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "addModerators",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def demote_moderators(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Removes moderator role from members in channels matching the filter.

        :param filter: The filter to match channels.
        :param members: List of members to demote from moderators.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "demoteModerators",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def assign_roles(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Assigns roles to members in channels matching the filter.

        :param filter: The filter to match channels.
        :param members: List of members with roles to assign.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "assignRoles",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def hide(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Hides channels matching the filter for the specified members.

        :param filter: The filter to match channels.
        :param members: List of members for whom to hide channels.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "hide",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def show(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Shows channels matching the filter for the specified members.

        :param filter: The filter to match channels.
        :param members: List of members for whom to show channels.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "show",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def archive(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Archives channels matching the filter for the specified members.

        :param filter: The filter to match channels.
        :param members: List of members for whom to archive channels.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "archive",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def unarchive(
        self, filter: ChannelsBatchFilters, members: List[ChannelBatchMemberRequest]
    ) -> StreamResponse:
        """
        Unarchives channels matching the filter for the specified members.

        :param filter: The filter to match channels.
        :param members: List of members for whom to unarchive channels.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "unarchive",
            "filter": filter,
            "members": members,
        }
        return await self.client.update_channels_batch(options)

    async def update_data(
        self, filter: ChannelsBatchFilters, data: ChannelDataUpdate
    ) -> StreamResponse:
        """
        Updates data on channels matching the filter.

        :param filter: The filter to match channels.
        :param data: Channel data to update.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "updateData",
            "filter": filter,
            "data": data,
        }
        return await self.client.update_channels_batch(options)

    async def add_filter_tags(
        self, filter: ChannelsBatchFilters, tags: List[str]
    ) -> StreamResponse:
        """
        Adds filter tags to channels matching the filter.

        :param filter: The filter to match channels.
        :param tags: List of filter tags to add.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "addFilterTags",
            "filter": filter,
            "filter_tags_update": tags,
        }
        return await self.client.update_channels_batch(options)

    async def remove_filter_tags(
        self, filter: ChannelsBatchFilters, tags: List[str]
    ) -> StreamResponse:
        """
        Removes filter tags from channels matching the filter.

        :param filter: The filter to match channels.
        :param tags: List of filter tags to remove.
        :return: StreamResponse containing task_id.
        """
        options: ChannelsBatchOptions = {
            "operation": "removeFilterTags",
            "filter": filter,
            "filter_tags_update": tags,
        }
        return await self.client.update_channels_batch(options)
