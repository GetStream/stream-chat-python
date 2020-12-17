import json

from stream_chat.base.channel import ChannelInterface, add_user_id


class Channel(ChannelInterface):
    async def send_message(self, message, user_id):
        """
        Send a message to this channel

        :param message: the Message object
        :param user_id: the ID of the user that created the message
        :return: the Server Response
        """
        payload = {"message": add_user_id(message, user_id)}
        return await self.client.post(f"{self.url}/message", data=payload)

    async def send_event(self, event, user_id):
        """
        Send an event on this channel

        :param event: event data, ie {type: 'message.read'}
        :param user_id: the ID of the user sending the event
        :return: the Server Response
        """
        payload = {"event": add_user_id(event, user_id)}
        return await self.client.post(f"{self.url}/event", data=payload)

    async def send_reaction(self, message_id, reaction, user_id):
        """
        Send a reaction about a message

        :param message_id: the message id
        :param reaction: the reaction object, ie {type: 'love'}
        :param user_id: the ID of the user that created the reaction
        :return: the Server Response
        """
        payload = {"reaction": add_user_id(reaction, user_id)}
        return await self.client.post(f"messages/{message_id}/reaction", data=payload)

    async def delete_reaction(self, message_id, reaction_type, user_id):
        """
        Delete a reaction by user and type

        :param message_id: the id of the message from which te remove the reaction
        :param reaction_type: the type of reaction that should be removed
        :param user_id: the id of the user
        :return: the Server Response
        """
        return await self.client.delete(
            f"messages/{message_id}/reaction/{reaction_type}",
            params={"user_id": user_id},
        )

    async def create(self, user_id):
        """
        Create the channel

        :param user_id: the ID of the user creating this channel
        :return:
        """
        self.custom_data["created_by"] = {"id": user_id}
        return await self.query(watch=False, state=False, presence=False)

    async def query(self, **options):
        """
        Query the API for this channel, get messages, members or other channel fields

        :param options: the query options, check docs on https://getstream.io/chat/docs/
        :return: Returns a query response
        """
        payload = {"state": True, "data": self.custom_data, **options}

        url = f"channels/{self.channel_type}"
        if self.id is not None:
            url = f"{url}/{self.id}"

        state = await self.client.post(f"{url}/query", data=payload)

        if self.id is None:
            self.id = state["channel"]["id"]

        return state

    async def query_members(self, filter_conditions, sort=None, **options):
        """
        Query the API for this channel to filter, sort and paginate its members efficiently.

        :param filter_conditions: filters, checks docs on https://getstream.io/chat/docs/
        :param sort: sorting field and direction slice, check docs on https://getstream.io/chat/docs/
        :param options: pagination or members based channel searching details
        :return: Returns members response

        eg.
        channel.query_members(filter_conditions={"name": "tommaso"},
                              sort=[{"created_at": -1}, {"updated_at": 1}],
                              offset=0,
                              limit=10)
        """

        payload = {
            "id": self.id,
            "type": self.channel_type,
            "filter_conditions": filter_conditions,
            "sort": self.client.normalize_sort(sort),
            **options,
        }
        response = await self.client.get(
            "members", params={"payload": json.dumps(payload)}
        )
        return response["members"]

    async def update(self, channel_data, update_message=None):
        """
        Edit the channel's custom properties

        :param channel_data: the object to update the custom properties of this channel with
        :param update_message: optional update message
        :return: The server response
        """
        payload = {"data": channel_data, "message": update_message}
        return await self.client.post(self.url, data=payload)

    async def delete(self):
        """
        Delete the channel. Messages are permanently removed.

        :return: The server response
        """
        return await self.client.delete(self.url)

    async def truncate(self):
        """
        Removes all messages from the channel

        :return: The server response
        """
        return await self.client.post(f"{self.url}/truncate")

    async def add_members(self, user_ids):
        """
        Adds members to the channel

        :param user_ids: user IDs to add as members
        :return:
        """
        return await self.client.post(self.url, data={"add_members": user_ids})

    async def invite_members(self, user_ids):
        """
        invite members to the channel

        :param user_ids: user IDs to invite
        :return:
        """
        return await self.client.post(self.url, data={"invites": user_ids})

    async def add_moderators(self, user_ids):
        """
        Adds moderators to the channel

        :param user_ids: user IDs to add as moderators
        :return:
        """
        return await self.client.post(self.url, data={"add_moderators": user_ids})

    async def remove_members(self, user_ids):
        """
        Remove members from the channel

        :param user_ids: user IDs to remove from the member list
        :return:
        """
        return await self.client.post(self.url, data={"remove_members": user_ids})

    async def demote_moderators(self, user_ids):
        """
        Demotes moderators from the channel

        :param user_ids: user IDs to demote
        :return:
        """
        return await self.client.post(self.url, data={"demote_moderators": user_ids})

    async def mark_read(self, user_id, **data):
        """
        Send the mark read event for this user, only works if the `read_events` setting is enabled

        :param user_id: the user ID for the event
        :param data: additional data, ie {"message_id": last_message_id}
        :return: The server response
        """
        payload = add_user_id(data, user_id)
        return await self.client.post(f"{self.url}/read", data=payload)

    async def get_replies(self, parent_id, **options):
        """
        List the message replies for a parent message

        :param parent_id: The message parent id, ie the top of the thread
        :param options: Pagination params, ie {limit:10, id_lte: 10}
        :return: A response with a list of messages
        """
        return await self.client.get(f"messages/{parent_id}/replies", params=options)

    async def get_reactions(self, message_id, **options):
        """
        List the reactions, supports pagination

        :param message_id: The message id
        :param options: Pagination params, ie {"limit":10, "id_lte": 10}
        :return: A response with a list of reactions
        """
        return await self.client.get(f"messages/{message_id}/reactions", params=options)

    async def ban_user(self, target_id, **options):
        """
        Bans a user from this channel

        :param target_id: the ID of the user to ban
        :param options: additional ban options, ie {"timeout": 3600, "reason": "offensive language is not allowed here"}
        :return: The server response
        """
        return await self.client.ban_user(
            target_id, type=self.channel_type, id=self.id, **options
        )

    async def unban_user(self, target_id, **options):
        """
        Removes the ban for a user on this channel

        :param target_id: the ID of the user to unban
        :return: The server response
        """
        return await self.client.unban_user(
            target_id, type=self.channel_type, id=self.id, **options
        )

    async def accept_invite(self, user_id, **data):
        payload = add_user_id(data, user_id)
        payload["accept_invite"] = True
        response = await self.client.post(self.url, data=payload)
        self.custom_data = response["channel"]
        return response

    async def reject_invite(self, user_id, **data):
        payload = add_user_id(data, user_id)
        payload["reject_invite"] = True
        response = await self.client.post(self.url, data=payload)
        self.custom_data = response["channel"]
        return response

    async def send_file(self, url, name, user, content_type=None):
        return await self.client.send_file(
            f"{self.url}/file", url, name, user, content_type=content_type
        )

    async def send_image(self, url, name, user, content_type=None):
        return await self.client.send_file(
            f"{self.url}/image", url, name, user, content_type=content_type
        )

    async def delete_file(self, url):
        return await self.client.delete(f"{self.url}/file", {"url": url})

    async def delete_image(self, url):
        return await self.client.delete(f"{self.url}/image", {"url": url})

    async def hide(self, user_id):
        return await self.client.post(f"{self.url}/hide", data={"user_id": user_id})

    async def show(self, user_id):
        return await self.client.post(f"{self.url}/show", data={"user_id": user_id})
