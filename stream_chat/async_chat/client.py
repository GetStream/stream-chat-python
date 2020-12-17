import json
from types import TracebackType
from typing import Optional, Type
from urllib.parse import urlparse

import aiohttp
from aiofile import AIOFile
from aiohttp import FormData
from stream_chat.__pkg__ import __version__
from stream_chat.async_chat.channel import Channel
from stream_chat.base.client import StreamChatInterface
from stream_chat.base.exceptions import StreamAPIException


def get_user_agent():
    return "stream-python-client-aio-%s" % __version__


def get_default_header():
    base_headers = {
        "Content-type": "application/json",
        "X-Stream-Client": get_user_agent(),
    }
    return base_headers


class StreamChatAsync(StreamChatInterface):
    def __init__(self, api_key, api_secret, timeout=6.0, **options):
        super().__init__(
            api_key=api_key, api_secret=api_secret, timeout=timeout, **options
        )
        self.session = aiohttp.ClientSession()

    async def _parse_response(self, response):
        text = await response.text()
        try:
            parsed_result = json.loads(text) if text else {}
        except ValueError:
            raise StreamAPIException(text, response.status)
        if response.status >= 399:
            raise StreamAPIException(text, response.status)
        return parsed_result

    async def _make_request(self, method, relative_url, params=None, data=None):
        params = params or {}
        params = {
            k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()
        }
        data = data or {}
        serialized = None
        default_params = self.get_default_params()
        default_params.update(params)
        headers = get_default_header()
        headers["Authorization"] = self.auth_token
        headers["stream-auth-type"] = "jwt"

        url = f"{self.base_url}/{relative_url}"

        if method.__name__ in ["post", "put", "patch"]:
            serialized = json.dumps(data)

        async with method(
            url,
            data=serialized,
            headers=headers,
            params=default_params,
            timeout=self.timeout,
        ) as response:
            return await self._parse_response(response)

    async def put(self, relative_url, params=None, data=None):
        return await self._make_request(self.session.put, relative_url, params, data)

    async def post(self, relative_url, params=None, data=None):
        return await self._make_request(self.session.post, relative_url, params, data)

    async def get(self, relative_url, params=None):
        return await self._make_request(self.session.get, relative_url, params, None)

    async def delete(self, relative_url, params=None):
        return await self._make_request(self.session.delete, relative_url, params, None)

    async def patch(self, relative_url, params=None, data=None):
        return await self._make_request(self.session.patch, relative_url, params, data)

    async def update_app_settings(self, **settings):
        return await self.patch("app", data=settings)

    async def get_app_settings(self):
        return await self.get("app")

    async def update_users(self, users):
        return await self.post("users", data={"users": {u["id"]: u for u in users}})

    async def update_user(self, user):
        return await self.update_users([user])

    async def update_users_partial(self, updates):
        return await self.patch("users", data={"users": updates})

    async def update_user_partial(self, update):
        return await self.update_users_partial([update])

    async def delete_user(self, user_id, **options):
        return await self.delete(f"users/{user_id}", options)

    async def deactivate_user(self, user_id, **options):
        return await self.post(f"users/{user_id}/deactivate", data=options)

    async def reactivate_user(self, user_id, **options):
        return await self.post(f"users/{user_id}/reactivate", data=options)

    async def export_user(self, user_id, **options):
        return await self.get(f"users/{user_id}/export", options)

    async def ban_user(self, target_id, **options):
        data = {"target_user_id": target_id, **options}
        return await self.post("moderation/ban", data=data)

    async def unban_user(self, target_id, **options):
        params = {"target_user_id": target_id, **options}
        return await self.delete("moderation/ban", params)

    async def flag_message(self, target_id, **options):
        data = {"target_message_id": target_id, **options}
        return await self.post("moderation/flag", data=data)

    async def unflag_message(self, target_id, **options):
        data = {"target_message_id": target_id, **options}
        return await self.post("moderation/unflag", data=data)

    async def flag_user(self, target_id, **options):
        data = {"target_user_id": target_id, **options}
        return await self.post("moderation/flag", data=data)

    async def unflag_user(self, target_id, **options):
        data = {"target_user_id": target_id, **options}
        return await self.post("moderation/unflag", data=data)

    async def mute_user(self, target_id, user_id, **options):
        """
        Create a mute

        :param target_id: the user getting muted
        :param user_id: the user muting the target
        :param options: additional mute options
        :return:
        """
        data = {"target_id": target_id, "user_id": user_id, **options}
        return await self.post("moderation/mute", data=data)

    async def unmute_user(self, target_id, user_id):
        """
        Removes a mute

        :param target_id: the user getting un-muted
        :param user_id: the user muting the target
        :return:
        """

        data = {"target_id": target_id, "user_id": user_id}
        return await self.post("moderation/unmute", data=data)

    async def mark_all_read(self, user_id):
        return await self.post("channels/read", data={"user": {"id": user_id}})

    async def update_message(self, message):
        if message.get("id") is None:
            raise ValueError("message must have an id")
        return await self.post(f"messages/{message['id']}", data={"message": message})

    async def delete_message(self, message_id, **options):
        return await self.delete(f"messages/{message_id}", options)

    async def get_message(self, message_id):
        return await self.get(f"messages/{message_id}")

    async def query_users(self, filter_conditions, sort=None, **options):
        params = options.copy()
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return await self.get("users", params={"payload": json.dumps(params)})

    async def query_channels(self, filter_conditions, sort=None, **options):
        params = {"state": True, "watch": False, "presence": False}
        params.update(options)
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return await self.get("channels", params={"payload": json.dumps(params)})

    async def create_channel_type(self, data):
        if "commands" not in data or not data["commands"]:
            data["commands"] = ["all"]
        return await self.post("channeltypes", data=data)

    async def get_channel_type(self, channel_type):
        return await self.get(f"channeltypes/{channel_type}")

    async def list_channel_types(self):
        return await self.get("channeltypes")

    async def update_channel_type(self, channel_type, **settings):
        return await self.put(f"channeltypes/{channel_type}", data=settings)

    async def delete_channel_type(self, channel_type):
        """
        Delete a type of channel

        :param channel_type: the channel type
        :return:
        """
        return await self.delete(f"channeltypes/{channel_type}")

    def channel(self, channel_type, channel_id=None, data=None):
        """
        Creates a channel object

        :param channel_type: the channel type
        :param channel_id: the id of the channel
        :param data: additional data, ie: {"members":[id1, id2, ...]}
        :return: Channel
        """
        return Channel(self, channel_type, channel_id, data)

    async def list_commands(self):
        return await self.get("commands")

    async def create_command(self, data):
        return await self.post("commands", data=data)

    async def delete_command(self, name):
        return await self.delete(f"commands/{name}")

    async def get_command(self, name):
        return await self.get(f"commands/{name}")

    async def update_command(self, name, **settings):
        return await self.put(f"commands/{name}", data=settings)

    async def add_device(self, device_id, push_provider, user_id):
        """
        Add a device to a user

        :param device_id: the id of the device
        :param push_provider: the push provider used (apn or firebase)
        :param user_id: the id of the user
        :return:
        """
        return await self.post(
            "devices",
            data={"id": device_id, "push_provider": push_provider, "user_id": user_id},
        )

    async def delete_device(self, device_id, user_id):
        """
        Delete a device for a user

        :param device_id: the id of the device
        :param user_id: the id of the user
        :return:
        """
        return await self.delete("devices", {"id": device_id, "user_id": user_id})

    async def get_devices(self, user_id):
        """
        Get the list of devices for a user

        :param user_id: the id of the user
        :return: list of devices
        """
        return await self.get("devices", {"user_id": user_id})

    async def search(self, filter_conditions, query, **options):
        params = {**options, "filter_conditions": filter_conditions, "query": query}
        return await self.get("search", params={"payload": json.dumps(params)})

    async def send_file(self, uri, url, name, user, content_type=None):
        headers = {
            "Authorization": self.auth_token,
            "stream-auth-type": "jwt",
            "X-Stream-Client": get_user_agent(),
        }
        parts = urlparse(url)
        if parts[0] == "":
            async with AIOFile(url, "rb") as f:
                content = await f.read()
        else:
            async with self.session.get(
                url, headers={"User-Agent": "Mozilla/5.0"}
            ) as content_response:
                content = await content_response.read()
        data = FormData()
        data.add_field("user", json.dumps(user))
        data.add_field("file", content, filename=name, content_type=content_type)
        async with self.session.post(
            f"{self.base_url}/{uri}",
            params=self.get_default_params(),
            data=data,
            headers=headers,
        ) as response:
            return await self._parse_response(response)

    async def create_blocklist(self, name, words):
        """
        Create a blocklist

        :param name: the name of the blocklist
        :param words: list of blocked words
        :return:
        """
        return await self.post("blocklists", data={"name": name, "words": words})

    async def list_blocklists(self):
        """
        List blocklists

        :return: list of blocklists
        """
        return await self.get("blocklists")

    async def get_blocklist(self, name):
        """Get a blocklist by name

        :param name: the name of the blocklist
        :return: blocklist dict representation
        """
        return await self.get(f"blocklists/{name}")

    async def update_blocklist(self, name, words):
        """
        Update a blocklist

        :param name: the name of the blocklist
        :param words: the list of blocked words (replaces the current list)
        :return:
        """
        return await self.put(f"blocklists/{name}", data={"words": words})

    async def delete_blocklist(self, name):
        """Delete a blocklist by name

        :param: the name of the blocklist
        :return:
        """
        return await self.delete(f"blocklists/{name}")

    async def close(self):
        await self.session.close()

    async def __aenter__(self) -> "StreamChatAsync":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()
