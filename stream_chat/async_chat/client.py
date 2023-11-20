import datetime
import json
import sys
import warnings
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    Union,
)
from urllib.parse import urlparse

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

import aiohttp
from aiofile import AIOFile
from aiohttp import FormData

from stream_chat.__pkg__ import __version__
from stream_chat.async_chat.channel import Channel
from stream_chat.base.client import StreamChatInterface
from stream_chat.base.exceptions import StreamAPIException
from stream_chat.types.stream_response import StreamResponse


def get_user_agent() -> str:
    return f"stream-python-client-aio-{__version__}"


def get_default_header() -> Dict[str, str]:
    base_headers = {
        "Content-type": "application/json",
        "X-Stream-Client": get_user_agent(),
    }
    return base_headers


class StreamChatAsync(StreamChatInterface, AsyncContextManager):
    def __init__(
        self, api_key: str, api_secret: str, timeout: float = 6.0, **options: Any
    ):
        super().__init__(
            api_key=api_key, api_secret=api_secret, timeout=timeout, **options
        )
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            connector=aiohttp.TCPConnector(keepalive_timeout=59.0),
        )

    def set_http_session(self, session: aiohttp.ClientSession) -> None:
        """
        You can use your own `aiohttp.ClientSession` instance. This instance
        will be used for underlying HTTP requests.
        Make sure you set up a `base_url` for the session.
        """
        self.session = session

    async def _parse_response(self, response: aiohttp.ClientResponse) -> StreamResponse:
        text = await response.text()
        try:
            parsed_result = await response.json() if text else {}
        except aiohttp.ClientResponseError:
            raise StreamAPIException(text, response.status)
        if response.status >= 399:
            raise StreamAPIException(text, response.status)

        return StreamResponse(parsed_result, dict(response.headers), response.status)

    async def _make_request(
        self,
        method: Callable,
        relative_url: str,
        params: Dict = None,
        data: Any = None,
    ) -> StreamResponse:
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

        if method.__name__ in ["post", "put", "patch"]:
            serialized = json.dumps(data)

        async with method(
            "/" + relative_url.lstrip("/"),
            data=serialized,
            headers=headers,
            params=default_params,
            timeout=self.timeout,
        ) as response:
            return await self._parse_response(response)

    async def put(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> StreamResponse:
        return await self._make_request(self.session.put, relative_url, params, data)

    async def post(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> StreamResponse:
        return await self._make_request(self.session.post, relative_url, params, data)

    async def get(self, relative_url: str, params: Dict = None) -> StreamResponse:
        return await self._make_request(self.session.get, relative_url, params, None)

    async def delete(self, relative_url: str, params: Dict = None) -> StreamResponse:
        return await self._make_request(self.session.delete, relative_url, params, None)

    async def patch(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> StreamResponse:
        return await self._make_request(self.session.patch, relative_url, params, data)

    async def update_app_settings(self, **settings: Any) -> StreamResponse:
        return await self.patch("app", data=settings)

    async def get_app_settings(self) -> StreamResponse:
        return await self.get("app")

    async def update_users(self, users: List[Dict]) -> StreamResponse:
        warnings.warn(
            "This method is deprecated. Use upsert_users instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.upsert_users(users)

    async def update_user(self, user: Dict) -> StreamResponse:
        warnings.warn(
            "This method is deprecated. Use upsert_user instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.upsert_user(user)

    async def upsert_users(self, users: List[Dict]) -> StreamResponse:
        return await self.post("users", data={"users": {u["id"]: u for u in users}})

    async def upsert_user(self, user: Dict) -> StreamResponse:
        return await self.upsert_users([user])

    async def update_users_partial(self, updates: List[Dict]) -> StreamResponse:
        return await self.patch("users", data={"users": updates})

    async def update_user_partial(self, update: Dict) -> StreamResponse:
        return await self.update_users_partial([update])

    async def delete_user(self, user_id: str, **options: Any) -> StreamResponse:
        return await self.delete(f"users/{user_id}", options)

    async def delete_users(
        self, user_ids: Iterable[str], delete_type: str, **options: Any
    ) -> StreamResponse:
        return await self.post(
            "users/delete", data=dict(options, user=delete_type, user_ids=user_ids)
        )

    async def restore_users(self, user_ids: Iterable[str]) -> StreamResponse:
        return await self.post("users/restore", data={"user_ids": user_ids})

    async def deactivate_user(self, user_id: str, **options: Any) -> StreamResponse:
        return await self.post(f"users/{user_id}/deactivate", data=options)

    async def reactivate_user(self, user_id: str, **options: Any) -> StreamResponse:
        return await self.post(f"users/{user_id}/reactivate", data=options)

    async def export_user(self, user_id: str, **options: Any) -> StreamResponse:
        return await self.get(f"users/{user_id}/export", options)

    async def ban_user(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_user_id": target_id, **options}
        return await self.post("moderation/ban", data=data)

    async def shadow_ban(self, target_id: str, **options: Any) -> StreamResponse:
        return await self.ban_user(target_id, shadow=True, **options)

    async def remove_shadow_ban(self, target_id: str, **options: Any) -> StreamResponse:
        return await self.unban_user(target_id, shadow=True, **options)

    async def unban_user(self, target_id: str, **options: Any) -> StreamResponse:
        params = {"target_user_id": target_id, **options}
        return await self.delete("moderation/ban", params)

    async def query_banned_users(self, query_conditions: Dict) -> StreamResponse:
        return await self.get(
            "query_banned_users", params={"payload": json.dumps(query_conditions)}
        )

    async def run_message_action(self, message_id: str, data: Dict) -> StreamResponse:
        return await self.post(f"messages/{message_id}/action", data=data)

    async def flag_message(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_message_id": target_id, **options}
        return await self.post("moderation/flag", data=data)

    async def unflag_message(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_message_id": target_id, **options}
        return await self.post("moderation/unflag", data=data)

    async def query_message_flags(
        self, filter_conditions: Dict, **options: Any
    ) -> StreamResponse:
        params = {
            **options,
            "filter_conditions": filter_conditions,
        }
        return await self.get(
            "moderation/flags/message", params={"payload": json.dumps(params)}
        )

    async def flag_user(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_user_id": target_id, **options}
        return await self.post("moderation/flag", data=data)

    async def unflag_user(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_user_id": target_id, **options}
        return await self.post("moderation/unflag", data=data)

    async def _query_flag_reports(self, **options: Any) -> StreamResponse:
        """
        Note: Do not use this.
        It is present for internal usage only.
        This function can, and will, break and/or be removed at any point in time.
        """
        data = {"filter_conditions": options}
        return await self.post("moderation/reports", data=data)

    async def _review_flag_report(
        self, report_id: str, review_result: str, user_id: str, **details: Any
    ) -> StreamResponse:
        """
        Note: Do not use this.
        It is present for internal usage only.
        This function can, and will, break and/or be removed at any point in time.
        """
        data = {
            "review_result": review_result,
            "user_id": user_id,
            "review_details": details,
        }
        return await self.patch(f"moderation/reports/{report_id}", data=data)

    async def mute_users(
        self, target_ids: List[str], user_id: str, **options: Any
    ) -> StreamResponse:
        data = {"target_ids": target_ids, "user_id": user_id, **options}
        return await self.post("moderation/mute", data=data)

    async def mute_user(
        self, target_id: str, user_id: str, **options: Any
    ) -> StreamResponse:
        data = {"target_id": target_id, "user_id": user_id, **options}
        return await self.post("moderation/mute", data=data)

    async def unmute_user(self, target_id: str, user_id: str) -> StreamResponse:
        data = {"target_id": target_id, "user_id": user_id}
        return await self.post("moderation/unmute", data=data)

    async def unmute_users(self, target_ids: List[str], user_id: str) -> StreamResponse:
        data = {"target_ids": target_ids, "user_id": user_id}
        return await self.post("moderation/unmute", data=data)

    async def mark_all_read(self, user_id: str) -> StreamResponse:
        return await self.post("channels/read", data={"user": {"id": user_id}})

    async def translate_message(self, message_id: str, language: str) -> StreamResponse:
        return await self.post(
            f"messages/{message_id}/translate", data={"language": language}
        )

    async def pin_message(
        self, message_id: str, user_id: str, expiration: int = None
    ) -> StreamResponse:
        updates = {
            "set": {
                "pinned": True,
                "pin_expires": expiration,
            }
        }
        return await self.update_message_partial(message_id, updates, user_id)

    async def unpin_message(self, message_id: str, user_id: str) -> StreamResponse:
        updates = {
            "set": {
                "pinned": False,
            }
        }
        return await self.update_message_partial(message_id, updates, user_id)

    async def update_message(self, message: Dict) -> StreamResponse:
        if message.get("id") is None:
            raise ValueError("message must have an id")
        return await self.post(f"messages/{message['id']}", data={"message": message})

    async def update_message_partial(
        self, message_id: str, updates: Dict, user_id: str, **options: Any
    ) -> StreamResponse:
        data = updates.copy()
        if user_id:
            data["user"] = {"id": user_id}
        data.update(options)
        return await self.put(f"messages/{message_id}", data=data)

    async def delete_message(self, message_id: str, **options: Any) -> StreamResponse:
        return await self.delete(f"messages/{message_id}", options)

    async def get_message(self, message_id: str) -> StreamResponse:
        return await self.get(f"messages/{message_id}")

    async def query_users(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> StreamResponse:
        params = options.copy()
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return await self.get("users", params={"payload": json.dumps(params)})

    async def query_channels(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> StreamResponse:
        params: Dict[str, Any] = {"state": True, "watch": False, "presence": False}
        params.update(options)
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return await self.post("channels", data=params)

    async def create_channel_type(self, data: Dict) -> StreamResponse:
        if "commands" not in data or not data["commands"]:
            data["commands"] = ["all"]
        return await self.post("channeltypes", data=data)

    async def get_channel_type(self, channel_type: str) -> StreamResponse:
        return await self.get(f"channeltypes/{channel_type}")

    async def list_channel_types(self) -> StreamResponse:
        return await self.get("channeltypes")

    async def update_channel_type(
        self, channel_type: str, **settings: Any
    ) -> StreamResponse:
        return await self.put(f"channeltypes/{channel_type}", data=settings)

    async def delete_channel_type(self, channel_type: str) -> StreamResponse:
        return await self.delete(f"channeltypes/{channel_type}")

    def channel(  # type: ignore
        self, channel_type: str, channel_id: str = None, data: Dict = None
    ) -> Channel:
        return Channel(self, channel_type, channel_id, data)

    async def delete_channels(
        self, cids: Iterable[str], **options: Any
    ) -> StreamResponse:
        return await self.post("channels/delete", data=dict(options, cids=cids))

    async def list_commands(self) -> StreamResponse:
        return await self.get("commands")

    async def create_command(self, data: Dict) -> StreamResponse:
        return await self.post("commands", data=data)

    async def delete_command(self, name: str) -> StreamResponse:
        return await self.delete(f"commands/{name}")

    async def get_command(self, name: str) -> StreamResponse:
        return await self.get(f"commands/{name}")

    async def update_command(self, name: str, **settings: Any) -> StreamResponse:
        return await self.put(f"commands/{name}", data=settings)

    async def add_device(
        self,
        device_id: str,
        push_provider: str,
        user_id: str,
        push_provider_name: str = None,
    ) -> StreamResponse:
        return await self.post(
            "devices",
            data={
                "id": device_id,
                "push_provider": push_provider,
                "user_id": user_id,
                "push_provider_name": push_provider_name,
            },
        )

    async def delete_device(self, device_id: str, user_id: str) -> StreamResponse:
        return await self.delete("devices", {"id": device_id, "user_id": user_id})

    async def get_devices(self, user_id: str) -> StreamResponse:
        return await self.get("devices", {"user_id": user_id})

    async def get_rate_limits(
        self,
        server_side: bool = False,
        android: bool = False,
        ios: bool = False,
        web: bool = False,
        endpoints: Iterable[str] = None,
    ) -> StreamResponse:
        params = {}
        if server_side:
            params["server_side"] = "true"
        if android:
            params["android"] = "true"
        if ios:
            params["ios"] = "true"
        if web:
            params["web"] = "true"
        if endpoints:
            params["endpoints"] = ",".join(endpoints)

        return await self.get("rate_limits", params)

    async def search(
        self,
        filter_conditions: Dict,
        query: Union[str, Dict],
        sort: List[Dict] = None,
        **options: Any,
    ) -> StreamResponse:
        if "offset" in options:
            if sort or "next" in options:
                raise ValueError("cannot use offset with sort or next parameters")
        params = self.create_search_params(filter_conditions, query, sort, **options)
        return await self.get("search", params={"payload": json.dumps(params)})

    async def send_file(
        self, uri: str, url: str, name: str, user: Dict, content_type: str = None
    ) -> StreamResponse:
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
            "/" + uri.lstrip("/"),
            params=self.get_default_params(),
            data=data,
            headers=headers,
        ) as response:
            return await self._parse_response(response)

    async def create_blocklist(
        self, name: str, words: Iterable[str], type: str = "regular"
    ) -> StreamResponse:
        return await self.post(
            "blocklists", data={"name": name, "words": words, "type": type}
        )

    async def list_blocklists(self) -> StreamResponse:
        return await self.get("blocklists")

    async def get_blocklist(self, name: str) -> StreamResponse:
        return await self.get(f"blocklists/{name}")

    async def update_blocklist(self, name: str, words: Iterable[str]) -> StreamResponse:
        return await self.put(f"blocklists/{name}", data={"words": words})

    async def delete_blocklist(self, name: str) -> StreamResponse:
        return await self.delete(f"blocklists/{name}")

    async def check_push(self, push_data: Dict) -> StreamResponse:
        return await self.post("check_push", data=push_data)

    async def check_sqs(
        self, sqs_key: str = None, sqs_secret: str = None, sqs_url: str = None
    ) -> StreamResponse:
        data = {"sqs_key": sqs_key, "sqs_secret": sqs_secret, "sqs_url": sqs_url}
        return await self.post("check_sqs", data=data)

    async def check_sns(
        self, sns_key: str = None, sns_secret: str = None, sns_topic_arn: str = None
    ) -> StreamResponse:
        data = {
            "sns_key": sns_key,
            "sns_secret": sns_secret,
            "sns_topic_arn": sns_topic_arn,
        }
        return await self.post("check_sns", data=data)

    async def set_guest_user(self, guest_user: Dict) -> StreamResponse:
        return await self.post("guest", data=dict(user=guest_user))

    async def get_permission(self, id: str) -> StreamResponse:
        return await self.get(f"permissions/{id}")

    async def create_permission(self, permission: Dict) -> StreamResponse:
        return await self.post("permissions", data=permission)

    async def update_permission(self, id: str, permission: Dict) -> StreamResponse:
        return await self.put(f"permissions/{id}", data=permission)

    async def delete_permission(self, id: str) -> StreamResponse:
        return await self.delete(f"permissions/{id}")

    async def list_permissions(self) -> StreamResponse:
        return await self.get("permissions")

    async def create_role(self, name: str) -> StreamResponse:
        return await self.post("roles", data={"name": name})

    async def delete_role(self, name: str) -> StreamResponse:
        return await self.delete(f"roles/{name}")

    async def list_roles(self) -> StreamResponse:
        return await self.get("roles")

    async def create_segment(self, segment: Dict) -> StreamResponse:
        return await self.post("segments", data={"segment": segment})

    async def query_segments(self, **params: Any) -> StreamResponse:
        return await self.get("segments", params={"payload": json.dumps(params)})

    async def update_segment(self, segment_id: str, data: Dict) -> StreamResponse:
        return await self.put(f"segments/{segment_id}", data={"segment": data})

    async def delete_segment(self, segment_id: str) -> StreamResponse:
        return await self.delete(f"segments/{segment_id}")

    async def create_campaign(self, campaign: Dict) -> StreamResponse:
        return await self.post("campaigns", data={"campaign": campaign})

    async def query_campaigns(self, **params: Any) -> StreamResponse:
        return await self.get("campaigns", params={"payload": json.dumps(params)})

    async def update_campaign(self, campaign_id: str, data: Dict) -> StreamResponse:
        return await self.put(f"campaigns/{campaign_id}", data={"campaign": data})

    async def delete_campaign(self, campaign_id: str, **options: Any) -> StreamResponse:
        return await self.delete(f"campaigns/{campaign_id}", params=options)

    async def schedule_campaign(
        self, campaign_id: str, scheduled_for: int = None
    ) -> StreamResponse:
        return await self.patch(
            f"campaigns/{campaign_id}/schedule", data={"scheduled_for": scheduled_for}
        )

    async def query_recipients(self, **params: Any) -> StreamResponse:
        return await self.get("recipients", params={"payload": json.dumps(params)})

    async def stop_campaign(self, campaign_id: str) -> StreamResponse:
        return await self.patch(f"campaigns/{campaign_id}/stop")

    async def resume_campaign(self, campaign_id: str) -> StreamResponse:
        return await self.patch(f"campaigns/{campaign_id}/resume")

    async def test_campaign(
        self, campaign_id: str, users: Iterable[str]
    ) -> StreamResponse:
        return await self.post(f"campaigns/{campaign_id}/test", data={"users": users})

    async def revoke_tokens(
        self, since: Union[str, datetime.datetime]
    ) -> StreamResponse:
        if isinstance(since, datetime.datetime):
            since = since.isoformat()

        return await self.update_app_settings(revoke_tokens_issued_before=since)

    async def revoke_user_token(
        self, user_id: str, before: Union[str, datetime.datetime]
    ) -> StreamResponse:
        return await self.revoke_users_token([user_id], before)

    async def revoke_users_token(
        self, user_ids: Iterable[str], before: Union[str, datetime.datetime]
    ) -> StreamResponse:
        if isinstance(before, datetime.datetime):
            before = before.isoformat()

        updates = []
        for user_id in user_ids:
            updates.append(
                {"id": user_id, "set": {"revoke_tokens_issued_before": before}}
            )
        return await self.update_users_partial(updates)

    async def export_channel(
        self,
        channel_type: str,
        channel_id: str,
        messages_since: Union[str, datetime.datetime] = None,
        messages_until: Union[str, datetime.datetime] = None,
        **options: Any,
    ) -> StreamResponse:
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
            ],
            **options,
        )

    async def export_channels(
        self, channels: Iterable[Dict], **options: Any
    ) -> StreamResponse:
        return await self.post(
            "export_channels", data={"channels": channels, **options}
        )

    async def get_export_channel_status(self, task_id: str) -> StreamResponse:
        return await self.get(f"export_channels/{task_id}")

    async def get_task(self, task_id: str) -> StreamResponse:
        return await self.get(f"tasks/{task_id}")

    async def send_user_custom_event(self, user_id: str, event: Dict) -> StreamResponse:
        return await self.post(f"users/{user_id}/event", data={"event": event})

    async def upsert_push_provider(self, push_provider_config: Dict) -> StreamResponse:
        return await self.post(
            "push_providers", data={"push_provider": push_provider_config}
        )

    async def delete_push_provider(
        self, provider_type: str, name: str
    ) -> StreamResponse:
        return await self.delete(f"push_providers/{provider_type}/{name}")

    async def list_push_providers(self) -> StreamResponse:
        return await self.get("push_providers")

    async def create_import_url(self, filename: str) -> StreamResponse:
        return await self.post("import_urls", data={"filename": filename})

    async def create_import(
        self, path: str, mode: Literal["insert", "upsert"] = "upsert"
    ) -> StreamResponse:
        return await self.post("imports", data={"path": path, "mode": mode})

    async def get_import(self, id: str) -> StreamResponse:
        return await self.get(f"imports/{id}")

    async def list_imports(self, options: Dict = None) -> StreamResponse:
        return await self.get("imports", params=options)

    async def close(self) -> None:
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
