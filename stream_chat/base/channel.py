import abc
from typing import Any, Awaitable, Dict, Iterable, List, Optional, Union

from stream_chat.base.client import StreamChatInterface
from stream_chat.base.exceptions import StreamChannelException
from stream_chat.types.stream_response import StreamResponse


class ChannelInterface(abc.ABC):
    def __init__(
        self,
        client: StreamChatInterface,
        channel_type: str,
        channel_id: str = None,
        custom_data: Dict = None,
    ):
        self.channel_type = channel_type
        self.id = channel_id
        self.client = client
        self.custom_data = custom_data or {}

    @property
    def url(self) -> str:
        if self.id is None:
            raise StreamChannelException("channel does not have an id")
        return f"channels/{self.channel_type}/{self.id}"

    @property
    def cid(self) -> str:
        if self.id is None:
            raise StreamChannelException("channel does not have an id")
        return f"{self.channel_type}:{self.id}"

    @abc.abstractmethod
    def send_message(
        self, message: Dict, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Send a message to this channel

        :param message: the Message object
        :param user_id: the ID of the user that created the message
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def send_event(
        self, event: Dict, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Send an event on this channel

        :param event: event data, ie {type: 'message.read'}
        :param user_id: the ID of the user sending the event
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def send_reaction(
        self, message_id: str, reaction: Dict, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Send a reaction about a message

        :param message_id: the message id
        :param reaction: the reaction object, ie {type: 'love'}
        :param user_id: the ID of the user that created the reaction
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def delete_reaction(
        self, message_id: str, reaction_type: str, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a reaction by user and type

        :param message_id: the id of the message from which te remove the reaction
        :param reaction_type: the type of reaction that should be removed
        :param user_id: the id of the user
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def create(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create the channel

        :param user_id: the ID of the user creating this channel
        :return:
        """
        pass

    @abc.abstractmethod
    def get_messages(
        self, message_ids: List[str]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Gets many messages

        :param message_ids: list of message ids to returns
        :return:
        """
        pass

    @abc.abstractmethod
    def query(self, **options: Any) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Query the API for this channel, get messages, members or other channel fields

        :param options: the query options, check docs on https://getstream.io/chat/docs/
        :return: Returns a query response
        """
        pass

    @abc.abstractmethod
    def query_members(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> Union[List[Dict], Awaitable[List[Dict]]]:
        """
        Query the API for this channel to filter, sort and paginate its members efficiently.

        :param filter_conditions: filters, checks docs on https://getstream.io/chat/docs/
        :param sort: sorting field and direction slice, check docs on https://getstream.io/chat/docs/
        :param options: pagination or members based channel searching details
        :return: Returns members response

        eg.
        channel.query_members(filter_conditions={"name": "tommaso"},
                              sort=[{"field": "created_at", "direction": -1}],
                              offset=0,
                              limit=10)
        """
        pass

    @abc.abstractmethod
    def update(
        self, channel_data: Dict, update_message: Dict = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Edit the channel's custom properties

        :param channel_data: the object to update the custom properties of this channel with
        :param update_message: optional update message
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def update_partial(
        self, to_set: Dict = None, to_unset: Iterable[str] = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Update channel partially

        :param to_set: a dictionary of key/value pairs to set or to override
        :param to_unset: a list of keys to clear
        """
        pass

    @abc.abstractmethod
    def delete(
        self, hard: bool = False
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete the channel. Messages are permanently removed.

        :return: The server response
        """
        pass

    @abc.abstractmethod
    def truncate(
        self, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Removes all messages from the channel

        :param options: the query options, check docs on https://getstream.io/chat/docs/python/channel_delete/?language=python#truncating-a-channel
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def add_members(
        self, members: Iterable[Dict], message: Dict = None, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Adds members to the channel

        :param members: member objects to add
        :param message: An optional to show
        :param options: additional options such as hide_history
        :return:
        """
        pass

    @abc.abstractmethod
    def assign_roles(
        self, members: Iterable[Dict], message: Dict = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Assigns new roles to specified channel members

        :param members: member objects with role information
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def invite_members(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        invite members to the channel

        :param user_ids: user IDs to invite
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def add_moderators(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Adds moderators to the channel

        :param user_ids: user IDs to add as moderators
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def remove_members(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Remove members from the channel

        :param user_ids: user IDs to remove from the member list
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def demote_moderators(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Demotes moderators from the channel

        :param user_ids: user IDs to demote
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def mark_read(
        self, user_id: str, **data: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Send the mark read event for this user, only works if the `read_events` setting is enabled

        :param user_id: the user ID for the event
        :param data: additional data, ie {"message_id": last_message_id}
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def mark_unread(
        self, user_id: str, **data: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Marks channel as unread from a specific message or thread, if thread_id is provided in data
        a thread will be searched, otherwise a message.

        :param user_id: the user ID for the event
        :param data: additional data, ie {"message_id": last_message_id} or {"thread_id": thread_id}
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def get_replies(
        self, parent_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List the message replies for a parent message

        :param parent_id: The message parent id, ie the top of the thread
        :param options: Pagination params, ie {limit:10, id_lte: 10}
        :return: A response with a list of messages
        """
        pass

    @abc.abstractmethod
    def get_reactions(
        self, message_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List the reactions, supports pagination

        :param message_id: The message id
        :param options: Pagination params, ie {"limit":10, "id_lte": 10}
        :return: A response with a list of reactions
        """
        pass

    @abc.abstractmethod
    def ban_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Bans a user from this channel

        :param target_id: the ID of the user to ban
        :param options: additional ban options, ie {"timeout": 3600, "reason": "offensive language is not allowed here"}
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def unban_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Removes the ban for a user on this channel

        :param target_id: the ID of the user to unban
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def accept_invite(
        self, user_id: str, **data: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Accepts an invitation to this channel.
        """
        pass

    @abc.abstractmethod
    def reject_invite(
        self, user_id: str, **data: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Rejects an invitation to this channel.
        """
        pass

    @abc.abstractmethod
    def send_file(
        self, url: str, name: str, user: Dict, content_type: str = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Uploads a file.
        This functionality defaults to using the Stream CDN. If you would like, you can
        easily change the logic to upload to your own CDN of choice.
        """
        pass

    @abc.abstractmethod
    def send_image(
        self, url: str, name: str, user: Dict, content_type: str = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Uploads an image.
        Stream supported image types are: image/bmp, image/gif, image/jpeg, image/png, image/webp,
        image/heic, image/heic-sequence, image/heif, image/heif-sequence, image/svg+xml.
        You can set a more restrictive list for your application if needed.
        The maximum file size is 100MB.
        """
        pass

    @abc.abstractmethod
    def delete_file(self, url: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Deletes a file by file url.
        """
        pass

    @abc.abstractmethod
    def delete_image(
        self, url: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Deletes an image by image url.
        """
        pass

    @abc.abstractmethod
    def hide(self, user_id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Removes a channel from query channel requests for that user until a new message is added.
        Use `show` to cancel this operation.
        """
        pass

    @abc.abstractmethod
    def show(self, user_id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Shows a previously hidden channel.
        Use `hide` to hide a channel.
        """
        pass

    @abc.abstractmethod
    def mute(
        self, user_id: str, expiration: int = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Mutes a channel.
        Messages added to a muted channel will not trigger push notifications, nor change the
        unread count for the users that muted it. By default, mutes stay in place indefinitely
        until the user removes it; however, you can optionally set an expiration time. The list
        of muted channels and their expiration time is returned when the user connects.
        """
        pass

    @abc.abstractmethod
    def unmute(self, user_id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Unmutes a channel.
        Messages added to a muted channel will not trigger push notifications, nor change the
        unread count for the users that muted it. By default, mutes stay in place indefinitely
        until the user removes it; however, you can optionally set an expiration time. The list
        of muted channels and their expiration time is returned when the user connects.
        """
        pass

    @abc.abstractmethod
    def pin(self, user_id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Pins a channel
        Allows a user to pin the channel (only for themselves)
        """
        pass

    @abc.abstractmethod
    def unpin(self, user_id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Unpins a channel
        Allows a user to unpin the channel (only for themselves)
        """
        pass

    @abc.abstractmethod
    def archive(self, user_id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Pins a channel
        Allows a user to archive the channel (only for themselves)
        """
        pass

    @abc.abstractmethod
    def unarchive(
        self, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Unpins a channel
        Allows a user to unpin the channel (only for themselves)
        """
        pass

    @abc.abstractmethod
    def update_member_partial(
        self, user_id: str, to_set: Dict = None, to_unset: Iterable[str] = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Update channel member partially

        :param to_set: a dictionary of key/value pairs to set or to override
        :param to_unset: a list of keys to clear
        """
        pass

    @abc.abstractmethod
    def create_draft(
        self, message: Dict, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Creates or updates a draft message in a channel.

        :param message: The message object
        :param user_id: The ID of the user creating the draft
        :return: The Server Response
        """
        pass

    @abc.abstractmethod
    def delete_draft(
        self, user_id: str, parent_id: Optional[str] = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Deletes a draft message from a channel.

        :param user_id: The ID of the user who owns the draft
        :param parent_id: Optional ID of the parent message if this is a thread draft
        :return: The Server Response
        """
        pass

    @abc.abstractmethod
    def get_draft(
        self, user_id: str, parent_id: Optional[str] = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Retrieves a draft message from a channel.

        :param user_id: The ID of the user who owns the draft
        :param parent_id: Optional ID of the parent message if this is a thread draft
        :return: The Server Response
        """
        pass


def add_user_id(payload: Dict, user_id: str) -> Dict:
    return {**payload, "user": {"id": user_id}}
