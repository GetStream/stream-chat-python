import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import requests

from stream_chat.__pkg__ import __version__
from stream_chat.base.client import StreamChatInterface
from stream_chat.base.exceptions import StreamAPIException

from .channel import Channel


def get_user_agent():
    return "stream-python-client-%s" % __version__


def get_default_header():
    base_headers = {
        "Content-type": "application/json",
        "X-Stream-Client": get_user_agent(),
    }
    return base_headers


class StreamChat(StreamChatInterface):
    def __init__(self, api_key, api_secret, timeout=6.0, **options):
        super().__init__(
            api_key=api_key, api_secret=api_secret, timeout=timeout, **options
        )
        self.session = requests.Session()

    def _parse_response(self, response):
        try:
            parsed_result = json.loads(response.text) if response.text else {}
        except ValueError:
            raise StreamAPIException(response.text, response.status_code)
        if response.status_code >= 399:
            raise StreamAPIException(response.text, response.status_code)
        return parsed_result

    def _make_request(self, method, relative_url, params=None, data=None):
        params = params or {}
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

        response = method(
            url,
            data=serialized,
            headers=headers,
            params=default_params,
            timeout=self.timeout,
        )
        return self._parse_response(response)

    def put(self, relative_url, params=None, data=None):
        return self._make_request(self.session.put, relative_url, params, data)

    def post(self, relative_url, params=None, data=None):
        return self._make_request(self.session.post, relative_url, params, data)

    def get(self, relative_url, params=None):
        return self._make_request(self.session.get, relative_url, params, None)

    def delete(self, relative_url, params=None):
        return self._make_request(self.session.delete, relative_url, params, None)

    def patch(self, relative_url, params=None, data=None):
        return self._make_request(self.session.patch, relative_url, params, data)

    def update_app_settings(self, **settings):
        return self.patch("app", data=settings)

    def get_app_settings(self):
        return self.get("app")

    def update_users(self, users):
        return self.post("users", data={"users": {u["id"]: u for u in users}})

    def update_user(self, user):
        return self.update_users([user])

    def update_users_partial(self, updates):
        return self.patch("users", data={"users": updates})

    def update_user_partial(self, update):
        return self.update_users_partial([update])

    def delete_user(self, user_id, **options):
        return self.delete(f"users/{user_id}", options)

    def deactivate_user(self, user_id, **options):
        return self.post(f"users/{user_id}/deactivate", data=options)

    def reactivate_user(self, user_id, **options):
        return self.post(f"users/{user_id}/reactivate", data=options)

    def export_user(self, user_id, **options):
        return self.get(f"users/{user_id}/export", options)

    def ban_user(self, target_id, **options):
        data = {"target_user_id": target_id, **options}
        return self.post("moderation/ban", data=data)

    def unban_user(self, target_id, **options):
        params = {"target_user_id": target_id, **options}
        return self.delete("moderation/ban", params)

    def flag_message(self, target_id, **options):
        data = {"target_message_id": target_id, **options}
        return self.post("moderation/flag", data=data)

    def unflag_message(self, target_id, **options):
        data = {"target_message_id": target_id, **options}
        return self.post("moderation/unflag", data=data)

    def flag_user(self, target_id, **options):
        data = {"target_user_id": target_id, **options}
        return self.post("moderation/flag", data=data)

    def unflag_user(self, target_id, **options):
        data = {"target_user_id": target_id, **options}
        return self.post("moderation/unflag", data=data)

    def mute_user(self, target_id, user_id, **options):
        """
        Create a mute

        :param target_id: the user getting muted
        :param user_id: the user muting the target
        :param options: additional mute options
        :return:
        """
        data = {"target_id": target_id, "user_id": user_id, **options}
        return self.post("moderation/mute", data=data)

    def unmute_user(self, target_id, user_id):
        """
        Removes a mute

        :param target_id: the user getting un-muted
        :param user_id: the user muting the target
        :return:
        """

        data = {"target_id": target_id, "user_id": user_id}
        return self.post("moderation/unmute", data=data)

    def mark_all_read(self, user_id):
        return self.post("channels/read", data={"user": {"id": user_id}})

    def update_message(self, message):
        if message.get("id") is None:
            raise ValueError("message must have an id")
        return self.post(f"messages/{message['id']}", data={"message": message})

    def delete_message(self, message_id, **options):
        return self.delete(f"messages/{message_id}", options)

    def get_message(self, message_id):
        return self.get(f"messages/{message_id}")

    def query_users(self, filter_conditions, sort=None, **options):
        params = options.copy()
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return self.get("users", params={"payload": json.dumps(params)})

    def query_channels(self, filter_conditions, sort=None, **options):
        params = {"state": True, "watch": False, "presence": False}
        params.update(options)
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return self.get("channels", params={"payload": json.dumps(params)})

    def create_channel_type(self, data):
        if "commands" not in data or not data["commands"]:
            data["commands"] = ["all"]
        return self.post("channeltypes", data=data)

    def get_channel_type(self, channel_type):
        return self.get(f"channeltypes/{channel_type}")

    def list_channel_types(self):
        return self.get("channeltypes")

    def update_channel_type(self, channel_type, **settings):
        return self.put(f"channeltypes/{channel_type}", data=settings)

    def delete_channel_type(self, channel_type):
        """
        Delete a type of channel

        :param channel_type: the channel type
        :return:
        """
        return self.delete(f"channeltypes/{channel_type}")

    def channel(self, channel_type, channel_id=None, data=None):
        """
        Creates a channel object

        :param channel_type: the channel type
        :param channel_id: the id of the channel
        :param data: additional data, ie: {"members":[id1, id2, ...]}
        :return: Channel
        """
        return Channel(self, channel_type, channel_id, data)

    def list_commands(self):
        return self.get("commands")

    def create_command(self, data):
        return self.post("commands", data=data)

    def delete_command(self, name):
        return self.delete(f"commands/{name}")

    def get_command(self, name):
        return self.get(f"commands/{name}")

    def update_command(self, name, **settings):
        return self.put(f"commands/{name}", data=settings)

    def add_device(self, device_id, push_provider, user_id):
        """
        Add a device to a user

        :param device_id: the id of the device
        :param push_provider: the push provider used (apn or firebase)
        :param user_id: the id of the user
        :return:
        """
        return self.post(
            "devices",
            data={"id": device_id, "push_provider": push_provider, "user_id": user_id},
        )

    def delete_device(self, device_id, user_id):
        """
        Delete a device for a user

        :param device_id: the id of the device
        :param user_id: the id of the user
        :return:
        """
        return self.delete("devices", {"id": device_id, "user_id": user_id})

    def get_devices(self, user_id):
        """
        Get the list of devices for a user

        :param user_id: the id of the user
        :return: list of devices
        """
        return self.get("devices", {"user_id": user_id})

    def search(self, filter_conditions, query, **options):
        params = {**options, "filter_conditions": filter_conditions, "query": query}
        return self.get("search", params={"payload": json.dumps(params)})

    def send_file(self, uri, url, name, user, content_type=None):
        headers = {
            "Authorization": self.auth_token,
            "stream-auth-type": "jwt",
            "X-Stream-Client": get_user_agent(),
        }
        parts = urlparse(url)
        if parts[0] == "":
            url = "file://" + url
        content = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()
        response = requests.post(
            f"{self.base_url}/{uri}",
            params=self.get_default_params(),
            data={"user": json.dumps(user)},
            files={"file": (name, content, content_type)},
            headers=headers,
        )
        return self._parse_response(response)

    def create_blocklist(self, name, words):
        """
        Create a blocklist

        :param name: the name of the blocklist
        :param words: list of blocked words
        :return:
        """
        return self.post("blocklists", data={"name": name, "words": words})

    def list_blocklists(self):
        """
        List blocklists

        :return: list of blocklists
        """
        return self.get("blocklists")

    def get_blocklist(self, name):
        """Get a blocklist by name

        :param name: the name of the blocklist
        :return: blocklist dict representation
        """
        return self.get(f"blocklists/{name}")

    def update_blocklist(self, name, words):
        """
        Update a blocklist

        :param name: the name of the blocklist
        :param words: the list of blocked words (replaces the current list)
        :return:
        """
        return self.put(f"blocklists/{name}", data={"words": words})

    def delete_blocklist(self, name):
        """Delete a blocklist by name

        :param: the name of the blocklist
        :return:
        """
        return self.delete(f"blocklists/{name}")
