from stream_chat.exceptions import StreamChannelException


class Channel(object):
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
        return "channels/{}/{}".format(self.channel_type, self.id)

    def send_message(self, message, user_id):
        """
        Send a message to this channel

        :param message: the Message object
        :param user_id: the ID of the user that created the message
        :return: the Server Response
        """
        payload = {"message": add_user_id(message, user_id)}
        return self.client.post("{}/message".format(self.url), data=payload)

    def send_event(self, event, user_id):
        """
        Send an event on this channel

        :param event: event data, ie {type: 'message.read'}
        :param user_id: the ID of the user sending the event
        :return: the Server Response
        """
        payload = {"event": add_user_id(event, user_id)}
        return self.client.post("{}/event".format(self.url), data=payload)

    def send_reaction(self, message_id, reaction, user_id):
        """
        Send a reaction about a message

        :param message_id: the message id
        :param reaction: the reaction object, ie {type: 'love'}
        :param user_id: the ID of the user that created the reaction
        :return: the Server Response
        """
        payload = {"reaction": add_user_id(reaction, user_id)}
        return self.client.post("messages/{}/reaction".format(message_id), data=payload)

    def delete_reaction(self, message_id, reaction_type, user_id):
        """
        Delete a reaction by user and type

        :param message_id: the id of the message from which te remove the reaction
        :param reaction_type: the type of reaction that should be removed
        :param user_id: the id of the user
        :return: the Server Response
        """
        return self.client.delete(
            "messages/{}/reaction/{}".format(message_id, reaction_type),
            params={"user_id": user_id},
        )

    def create(self, user_id):
        """
        Create the channel

        :param user_id: the ID of the user creating this channel
        :return:
        """
        self.custom_data["created_by"] = dict(id=user_id)
        return self.query(watch=False, state=False, presence=False)

    def query(self, **options):
        """
        Query the API for this channel, get messages, members or other channel fields

        :param options: the query options, check docs on https://getstream.io/chat/docs/
        :return: Returns a query response
        """
        payload = {"state": True, "data": self.custom_data}
        payload.update(options)

        url = "channels/{}".format(self.channel_type)
        if self.id is not None:
            url = "{}/{}".format(url, self.id)

        state = self.client.post("{}/query".format(url), data=payload)

        if self.id is None:
            self.id = state["channel"]["id"]

        return state

    def update(self, channel_data, update_message=None):
        """
        Edit the channel's custom properties

        :param channel_data: the object to update the custom properties of this channel with
        :param update_message: optional update message
        :return: The server response
        """
        payload = {"data": channel_data, "message": update_message}
        return self.client.post(self.url, data=payload)

    def delete(self):
        """
        Delete the channel. Messages are permanently removed.

        :return: The server response
        """
        return self.client.delete(self.url)

    def truncate(self):
        """
        Removes all messages from the channel

        :return: The server response
        """
        return self.client.post("{}/truncate".format(self.url))

    def add_members(self, user_ids):
        """
        Adds members to the channel

        :param user_ids: user IDs to add as members
        :return:
        """
        return self.client.post(self.url, data={"add_members": user_ids})

    def add_moderators(self, user_ids):
        """
        Adds moderators to the channel

        :param user_ids: user IDs to add as moderators
        :return:
        """
        return self.client.post(self.url, data={"add_moderators": user_ids})

    def remove_members(self, user_ids):
        """
        Remove members from the channel

        :param user_ids: user IDs to remove from the member list
        :return:
        """
        return self.client.post(self.url, data={"remove_members": user_ids})

    def demote_moderators(self, user_ids):
        """
        Demotes moderators from the channel

        :param user_ids: user IDs to demote
        :return:
        """
        return self.client.post(self.url, data={"demote_moderators": user_ids})

    def mark_read(self, user_id, **data):
        """
        Send the mark read event for this user, only works if the `read_events` setting is enabled

        :param user_id: the user ID for the event
        :param data: additional data, ie {"message_id": last_message_id}
        :return: The server response
        """
        payload = add_user_id(data, user_id)
        return self.client.post("{}/read".format(self.url), data=payload)

    def get_replies(self, parent_id, **options):
        """
        List the message replies for a parent message

        :param parent_id: The message parent id, ie the top of the thread
        :param options: Pagination params, ie {limit:10, idlte: 10}
        :return: A response with a list of messages
        """
        return self.client.get("messages/{}/replies".format(parent_id), params=options)

    def get_reactions(self, message_id, **options):
        """
        List the reactions, supports pagination

        :param message_id: The message id
        :param options: Pagination params, ie {"limit":10, "idlte": 10}
        :return: A response with a list of reactions
        """
        return self.client.get("messages/{}/reactions".format(message_id), params=options)

    def ban_user(self, user_id, **options):
        """
        Bans a user from this channel

        :param user_id: the ID of the user to ban
        :param options: additional ban options, ie {"timeout": 3600, "reason": "offensive language is not allowed here"}
        :return: The server response
        """
        return self.client.ban_user(
            user_id, type=self.channel_type, id=self.id, **options
        )

    def unban_user(self, user_id):
        """
        Removes the ban for a user on this channel

        :param user_id: the ID of the user to unban
        :return: The server response
        """
        return self.client.unban_user(user_id, type=self.channel_type, id=self.id)

    def accept_invite(self, user_id):
        raise NotImplementedError

    def reject_invite(self, user_id):
        raise NotImplementedError

    def send_file(self):
        raise NotImplementedError

    def send_image(self):
        raise NotImplementedError

    def delete_file(self):
        raise NotImplementedError

    def delete_image(self):
        raise NotImplementedError


def add_user_id(payload, user_id):
    payload = payload.copy()
    payload.update(dict(user=dict(id=user_id)))
    return payload
