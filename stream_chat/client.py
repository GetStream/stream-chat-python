from urllib.parse import urlparse
import hmac
import hashlib
import json
import urllib
from urllib.request import Request, urlopen

import jwt
import requests

from stream_chat.__pkg__ import __version__
from stream_chat.channel import Channel
from stream_chat.exceptions import StreamAPIException


def get_user_agent():
    return "stream-python-client-%s" % __version__


def get_default_header():
    base_headers = {
        "Content-type": "application/json",
        "X-Stream-Client": get_user_agent(),
    }
    return base_headers


class StreamChat(object):
    def __init__(self, api_key, api_secret, timeout=6.0, **options):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.options = options
        self.base_url = options.get(
            "base_url", "https://chat-us-east-1.stream-io-api.com"
        )
        self.auth_token = jwt.encode(
            {"server": True}, self.api_secret, algorithm="HS256"
        )
        self.session = requests.Session()

    def get_default_params(self):
        return {"api_key": self.api_key}

    def _parse_response(self, response):
        try:
            parsed_result = json.loads(response.text) if response.text else {}
        except ValueError:
            raise StreamAPIException(response)
        if response.status_code >= 399:
            raise StreamAPIException(response)
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

        url = "{}/{}".format(self.base_url, relative_url)

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

    def create_token(self, user_id, exp=None):
        payload = {"user_id": user_id}
        if exp is not None:
            payload["exp"] = exp
        return jwt.encode(payload, self.api_secret, algorithm="HS256").decode()

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
        return self.delete("users/{}".format(user_id), options)

    def deactivate_user(self, user_id, **options):
        return self.post("users/{}/deactivate".format(user_id), data=options)

    def reactivate_user(self, user_id, **options):
        return self.post("users/{}/reactivate".format(user_id), data=options)

    def export_user(self, user_id, **options):
        return self.get("users/{}/export".format(user_id), options)

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
        return self.post("messages/{}".format(message["id"]), data={"message": message})

    def delete_message(self, message_id, **options):
        return self.delete("messages/{}".format(message_id), options)

    def get_message(self, message_id):
        return self.get("messages/{}".format(message_id))

    def query_users(self, filter_conditions, sort=None, **options):
        sort_fields = []
        if sort is not None:
            sort_fields = [{"field": k, "direction": v} for k, v in sort.items()]
        params = options.copy()
        params.update({"filter_conditions": filter_conditions, "sort": sort_fields})
        return self.get("users", params={"payload": json.dumps(params)})

    def query_channels(self, filter_conditions, sort=None, **options):
        params = {"state": True, "watch": False, "presence": False}
        sort_fields = []
        if sort is not None:
            sort_fields = [{"field": k, "direction": v} for k, v in sort.items()]
        params.update(options)
        params.update({"filter_conditions": filter_conditions, "sort": sort_fields})
        return self.get("channels", params={"payload": json.dumps(params)})

    def create_channel_type(self, data):
        if "commands" not in data or not data["commands"]:
            data["commands"] = ["all"]
        return self.post("channeltypes", data=data)

    def get_channel_type(self, channel_type):
        return self.get("channeltypes/{}".format(channel_type))

    def list_channel_types(self):
        return self.get("channeltypes")

    def update_channel_type(self, channel_type, **settings):
        return self.put("channeltypes/{}".format(channel_type), data=settings)

    def delete_channel_type(self, channel_type):
        """
        Delete a type of channel

        :param channel_type: the channel type
        :return:
        """
        return self.delete("channeltypes/{}".format(channel_type))

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
        return self.delete("commands/{}".format(name))

    def get_command(self, name):
        return self.get("commands/{}".format(name))

    def update_command(self, name, **settings):
        return self.put("commands/{}".format(name), data=settings)

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

    def verify_webhook(self, request_body, x_signature):
        """
        Verify the signature added to a webhook event

        :param request_body: the request body received from webhook
        :param x_signature: the x-signature header included in the request
        :return: bool
        """
        signature = hmac.new(
            key=self.api_secret.encode(), msg=request_body, digestmod=hashlib.sha256
        ).hexdigest()
        return signature == x_signature

    def search(self, filter_conditions, query, **options):
        params = {**options, "filter_conditions": filter_conditions, "query": query}
        return self.get("search", params={"payload": json.dumps(params)})

    def send_file(self, uri, url, name, user, content_type=None):
        headers = {}
        headers["Authorization"] = self.auth_token
        headers["stream-auth-type"] = "jwt"
        headers["X-Stream-Client"] = get_user_agent()
        parts = urlparse(url)
        if parts[0] == "":
            url = "file://" + url
        content = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()
        response = requests.post(
            "{}/{}".format(self.base_url, uri),
            params=self.get_default_params(),
            data={"user": json.dumps(user)},
            files={"file": (name, content, content_type)},
            headers=headers,
        )
        return self._parse_response(response)
