import json
import datetime
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

    async def query_message_flags(self, filter_conditions, **options):
        params = {
            **options,
            "filter_conditions": filter_conditions,
        }
        return await self.get(
            "moderation/flags/message", params={"payload": json.dumps(params)}
        )

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

    async def get_rate_limits(
        self, server_side=False, android=False, ios=False, web=False, endpoints=None
    ):
        """
        Get rate limit quotas and usage.
        If no params are toggled, all limits for all endpoints are returned.

        :param server_side: if true, show server_side limits.
        :param android: if true, show android limits.
        :param ios: if true, show ios limits.
        :param web: if true, show web limits.
        :param endpoints: restrict returned limits to the given list of endpoints.
        """
        params = {}
        if server_side:
            params["server_side"] = "true"
        if android:
            params["android"] = "true"
        if ios:
            params["ios"] = "true"
        if web:
            params["web"] = "true"
        if endpoints is not None and len(endpoints) > 0:
            params["endpoints"] = ",".join(endpoints)

        return await self.get("rate_limits", params)

    async def search(self, filter_conditions, query, sort=None, **options):
        if "offset" in options:
            if sort or "next" in options:
                raise ValueError("cannot use offset with sort or next parameters")
        params = self.create_search_params(filter_conditions, query, sort, **options)
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

    async def check_sqs(self, sqs_key=None, sqs_secret=None, sqs_url=None):
        """
        Check SQS Push settings

        When no parameters are given, the current SQS app settings are used

        :param sqs_key: AWS access key
        :param sqs_secret: AWS secret key
        :param sqs_url: URL to SQS queue
        :return:
        """
        data = {"sqs_key": sqs_key, "sqs_secret": sqs_secret, "sqs_url": sqs_url}
        return await self.post("check_sqs", data=data)

    async def get_permission(self, id):
        """
        Get the definition for a permission

        :param id: ID of the permission
        """
        return await self.get(f"permissions/{id}")

    async def create_permission(self, permission):
        """
        Create a custom permission

        :param permission: Definition of the permission
        """
        return await self.post("permissions", data=permission)

    async def update_permission(self, id, permission):
        """
        Update a custom permission

        :param id: ID of the permission
        :param permission: New definition of the permission
        """
        return await self.put(f"permissions/{id}", data=permission)

    async def delete_permission(self, id):
        """
        Delete a custom permission

        :param id: ID of the permission
        """
        return await self.delete(f"permissions/{id}")

    async def list_permissions(self):
        """
        List all permissions of the app
        """
        return await self.get("permissions")

    async def create_role(self, name):
        """
        Create a custom role

        :param name: Name of the role
        """
        return await self.post("roles", data={"name": name})

    async def delete_role(self, name):
        """
        Delete a custom role

        :param name: Name of the role
        """
        return await self.delete(f"roles/{name}")

    async def list_roles(self):
        """
        List all roles of the app
        """
        return await self.get("roles")

    async def create_segment(self, segment):
        """
        Create a segment
        """
        return await self.post("segments", data={"segment": segment})

    async def get_segment(self, segment_id):
        """
        Get a segment by id
        """
        return await self.get(f"segments/{segment_id}")

    async def list_segments(self, **params):
        """
        List segments
        """
        return await self.get("segments", params)

    async def update_segment(self, segment_id, data):
        """
        Update a segment by id
        """
        return await self.put(f"segments/{segment_id}", data=data)

    async def delete_segment(self, segment_id):
        """
        Delete a segment by id
        """
        return await self.delete(f"segments/{segment_id}")

    async def create_campaign(self, campaign):
        """
        Create a campaign
        """
        return await self.post("campaigns", data={"campaign": campaign})

    async def get_campaign(self, campaign_id):
        """
        Get a campaign by id
        """
        return await self.get(f"campaigns/{campaign_id}")

    async def list_campaigns(self, **params):
        """
        List campaigns
        """
        return await self.get("campaigns", params)

    async def update_campaign(self, campaign_id, data):
        """
        Update a campaign
        """
        return await self.put(f"campaigns/{campaign_id}", data=data)

    async def delete_campaign(self, campaign_id):
        """
        Delete a campaign by id
        """
        return await self.delete(f"campaigns/{campaign_id}")

    async def schedule_campaign(self, campaign_id, send_at=None):
        """
        Schedule a campaign at given time
        """
        return await self.patch(
            f"campaigns/{campaign_id}/schedule", data={"send_at": send_at}
        )

    async def stop_campaign(self, campaign_id):
        """
        Stop a in progress campaign
        """
        return await self.patch(f"campaigns/{campaign_id}/stop")

    async def resume_campaign(self, campaign_id):
        """
        Resume a stopped campaign
        """
        return await self.patch(f"campaigns/{campaign_id}/resume")

    async def test_campaign(self, campaign_id, users):
        """
        Trigger a test send of the given campaing to given users
        """
        return await self.post(f"campaigns/{campaign_id}/test", data={"users": users})

    async def revoke_tokens(self, before):
        """
        Revokes tokens for an application
        :param before: date before which the tokens are to be revoked, pass None to reset
        """
        if isinstance(before, datetime.datetime):
            before = before.isoformat()

        await self.update_app_settings({"revoke_tokens_issued_before": before})

    async def revoke_user_token(self, user_id, before):
        """
        Revokes token for a user
        :param user_id: user_id of user for which the token needs to be revoked
        :param before: date before which the tokens are to be revoked, , pass None to reset
        """
        await self.revoke_users_token([user_id], before)

    async def revoke_users_token(self, user_ids, before):
        """
        Revokes tokens for given users
        :param user_ids: user_ids for user for whom the token needs to be revoked
        :param before: date before which the tokens are to be revoked, pass None to reset
        """
        if isinstance(before, datetime.datetime):
            before = before.isoformat()

        updates = []
        for user_id in user_ids:
            updates.append(
                {"id": user_id, "set": {"revoke_tokens_issued_before": before}}
            )
        await self.update_users_partial(updates)

    async def export_channel(
        self,
        channel_type,
        channel_id,
        messages_since=None,
        messages_until=None,
    ):
        """
        Requests a channel export
        :param channel_type: channel_type of channel which needs to be exported
        :param channel_id: channel_id of channel which needs to be exported
        :param messages_since: RFC-3339 string or datetime to filter messages since that time, optional
        :param messages_until: RFC-3339 string or datetime to filter messages until that time, optional
        :type channel_id: str
        :type channel_type: str
        :type messages_since: Union[str, datetime.datetime]
        :type messages_until: Union[str, datetime.datetime]
        """
        if isinstance(messages_since, datetime.datetime):
            messages_since = messages_since.isoformat()
        if isinstance(messages_until, datetime.datetime):
            messages_until = messages_until.isoformat()

        return await self.export_channels(
            [
                {
                    "id": channel_id,
                    "type": channel_type,
                    "messages_since": messages_since,
                    "messages_until": messages_until,
                }
            ]
        )

    async def export_channels(self, channels):
        """
        Requests a channels export
        :param channels_data: list of channel's data which need to be exported with keys:
        - `channel_type`: str
        - `channel_id`: str
        - `messages_since` (optional, nullable): str
        - `messages_until` (optional, nullable): str
        :type channels_data: List[Dict[str, str]]
        """
        return await self.post("export_channels", data={"channels": channels})

    async def get_export_channel_status(self, task_id: str):
        """
        Retrieves status of export
        :param task_id: task_id of task which status needs to be retrieved
        :type task_id: str
        """
        return await self.get(f"export_channels/{task_id}")

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
