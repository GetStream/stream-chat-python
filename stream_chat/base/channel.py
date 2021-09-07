import abc

from stream_chat.base.exceptions import StreamChannelException


class ChannelInterface(abc.ABC):
    def __init__(self, client, channel_type, channel_id=None, custom_data=None):
        self.channel_type = channel_type
        self.id = channel_id
        self.client = client
        self.custom_data = custom_data
        if self.custom_data is None:
            self.custom_data = {}

    @property
    def url(self):
        if self.id is None:
            raise StreamChannelException("channel does not have an id")
        return f"channels/{self.channel_type}/{self.id}"

    @property
    def cid(self):
        if self.id is None:
            raise StreamChannelException("channel does not have an id")
        return f"{self.channel_type}:{self.id}"

    @abc.abstractmethod
    def send_message(self, message, user_id, **options):
        """
        Send a message to this channel

        :param message: the Message object
        :param user_id: the ID of the user that created the message
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def send_event(self, event, user_id):
        """
        Send an event on this channel

        :param event: event data, ie {type: 'message.read'}
        :param user_id: the ID of the user sending the event
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def send_reaction(self, message_id, reaction, user_id):
        """
        Send a reaction about a message

        :param message_id: the message id
        :param reaction: the reaction object, ie {type: 'love'}
        :param user_id: the ID of the user that created the reaction
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def delete_reaction(self, message_id, reaction_type, user_id):
        """
        Delete a reaction by user and type

        :param message_id: the id of the message from which te remove the reaction
        :param reaction_type: the type of reaction that should be removed
        :param user_id: the id of the user
        :return: the Server Response
        """
        pass

    @abc.abstractmethod
    def create(self, user_id):
        """
        Create the channel

        :param user_id: the ID of the user creating this channel
        :return:
        """
        pass

    @abc.abstractmethod
    def query(self, **options):
        """
        Query the API for this channel, get messages, members or other channel fields

        :param options: the query options, check docs on https://getstream.io/chat/docs/
        :return: Returns a query response
        """
        pass

    @abc.abstractmethod
    def query_members(self, filter_conditions, sort=None, **options):
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
    def update(self, channel_data, update_message=None):
        """
        Edit the channel's custom properties

        :param channel_data: the object to update the custom properties of this channel with
        :param update_message: optional update message
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def update_partial(self, to_set=None, to_unset=None):
        """
        Update channel partially

        :param to_set: a dictionary of key/value pairs to set or to override
        :param to_unset: a list of keys to clear
        """
        pass

    @abc.abstractmethod
    def delete(self):
        """
        Delete the channel. Messages are permanently removed.

        :return: The server response
        """
        pass

    @abc.abstractmethod
    def truncate(self):
        """
        Removes all messages from the channel

        :return: The server response
        """
        pass

    @abc.abstractmethod
    def add_members(self, user_ids, message=None):
        """
        Adds members to the channel

        :param user_ids: user IDs to add as members
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def invite_members(self, user_ids, message=None):
        """
        invite members to the channel

        :param user_ids: user IDs to invite
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def add_moderators(self, user_ids, message=None):
        """
        Adds moderators to the channel

        :param user_ids: user IDs to add as moderators
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def remove_members(self, user_ids, message=None):
        """
        Remove members from the channel

        :param user_ids: user IDs to remove from the member list
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def demote_moderators(self, user_ids, message=None):
        """
        Demotes moderators from the channel

        :param user_ids: user IDs to demote
        :param message: An optional to show
        :return:
        """
        pass

    @abc.abstractmethod
    def mark_read(self, user_id, **data):
        """
        Send the mark read event for this user, only works if the `read_events` setting is enabled

        :param user_id: the user ID for the event
        :param data: additional data, ie {"message_id": last_message_id}
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def get_replies(self, parent_id, **options):
        """
        List the message replies for a parent message

        :param parent_id: The message parent id, ie the top of the thread
        :param options: Pagination params, ie {limit:10, id_lte: 10}
        :return: A response with a list of messages
        """
        pass

    @abc.abstractmethod
    def get_reactions(self, message_id, **options):
        """
        List the reactions, supports pagination

        :param message_id: The message id
        :param options: Pagination params, ie {"limit":10, "id_lte": 10}
        :return: A response with a list of reactions
        """
        pass

    @abc.abstractmethod
    def ban_user(self, target_id, **options):
        """
        Bans a user from this channel

        :param target_id: the ID of the user to ban
        :param options: additional ban options, ie {"timeout": 3600, "reason": "offensive language is not allowed here"}
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def unban_user(self, target_id, **options):
        """
        Removes the ban for a user on this channel

        :param target_id: the ID of the user to unban
        :return: The server response
        """
        pass

    @abc.abstractmethod
    def accept_invite(self, user_id, **data):
        pass

    @abc.abstractmethod
    def reject_invite(self, user_id, **data):
        pass

    @abc.abstractmethod
    def send_file(self, url, name, user, content_type=None):
        pass

    @abc.abstractmethod
    def send_image(self, url, name, user, content_type=None):
        pass

    @abc.abstractmethod
    def delete_file(self, url):
        pass

    @abc.abstractmethod
    def delete_image(self, url):
        pass

    @abc.abstractmethod
    def hide(self, user_id):
        pass

    @abc.abstractmethod
    def show(self, user_id):
        pass

    @abc.abstractmethod
    def mute(self, user_id, expiration=None):
        pass

    @abc.abstractmethod
    def unmute(self, user_id):
        pass


def add_user_id(payload, user_id):
    return {**payload, "user": {"id": user_id}}
