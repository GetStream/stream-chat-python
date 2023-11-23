import datetime
import json
import sys
import warnings
from typing import Any, Callable, Dict, Iterable, List, Union
from urllib.parse import urlparse
from urllib.request import Request, urlopen

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


import requests

from stream_chat.__pkg__ import __version__
from stream_chat.base.client import StreamChatInterface
from stream_chat.base.exceptions import StreamAPIException
from stream_chat.channel import Channel
from stream_chat.types.stream_response import StreamResponse


def get_user_agent() -> str:
    return f"stream-python-client-{__version__}"


def get_default_header() -> Dict[str, str]:
    base_headers = {
        "Content-type": "application/json",
        "X-Stream-Client": get_user_agent(),
    }
    return base_headers


class StreamChat(StreamChatInterface):
    def __init__(
        self, api_key: str, api_secret: str, timeout: float = 6.0, **options: Any
    ):
        super().__init__(
            api_key=api_key, api_secret=api_secret, timeout=timeout, **options
        )
        self.session = requests.Session()
        self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=1))
        self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=1))

    def set_http_session(self, session: requests.Session) -> None:
        """
        You can use your own `requests.Session` instance. This instance
        will be used for underlying HTTP requests.
        """
        self.session = session

    def _parse_response(self, response: requests.Response) -> StreamResponse:
        try:
            parsed_result = json.loads(response.text) if response.text else {}
        except ValueError:
            raise StreamAPIException(response.text, response.status_code)
        if response.status_code >= 399:
            raise StreamAPIException(response.text, response.status_code)

        return StreamResponse(
            parsed_result, dict(response.headers), response.status_code
        )

    def _make_request(
        self,
        method: Callable[..., requests.Response],
        relative_url: str,
        params: Dict = None,
        data: Any = None,
    ) -> StreamResponse:
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

    def put(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> StreamResponse:
        return self._make_request(self.session.put, relative_url, params, data)

    def post(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> StreamResponse:
        return self._make_request(self.session.post, relative_url, params, data)

    def get(self, relative_url: str, params: Dict = None) -> StreamResponse:
        return self._make_request(self.session.get, relative_url, params, None)

    def delete(self, relative_url: str, params: Dict = None) -> StreamResponse:
        return self._make_request(self.session.delete, relative_url, params, None)

    def patch(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> StreamResponse:
        return self._make_request(self.session.patch, relative_url, params, data)

    def update_app_settings(self, **settings: Any) -> StreamResponse:
        return self.patch("app", data=settings)

    def get_app_settings(self) -> StreamResponse:
        return self.get("app")

    def set_guest_user(self, guest_user: Dict) -> StreamResponse:
        return self.post("guest", data=dict(user=guest_user))

    def update_users(self, users: List[Dict]) -> StreamResponse:
        warnings.warn(
            "This method is deprecated. Use upsert_users instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.upsert_users(users)

    def update_user(self, user: Dict) -> StreamResponse:
        warnings.warn(
            "This method is deprecated. Use upsert_user instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.upsert_user(user)

    def upsert_users(self, users: List[Dict]) -> StreamResponse:
        return self.post("users", data={"users": {u["id"]: u for u in users}})

    def upsert_user(self, user: Dict) -> StreamResponse:
        return self.upsert_users([user])

    def update_users_partial(self, updates: List[Dict]) -> StreamResponse:
        return self.patch("users", data={"users": updates})

    def update_user_partial(self, update: Dict) -> StreamResponse:
        return self.update_users_partial([update])

    def delete_user(self, user_id: str, **options: Any) -> StreamResponse:
        return self.delete(f"users/{user_id}", options)

    def delete_users(
        self, user_ids: Iterable[str], delete_type: str, **options: Any
    ) -> StreamResponse:
        return self.post(
            "users/delete", data=dict(options, user=delete_type, user_ids=user_ids)
        )

    def restore_users(self, user_ids: Iterable[str]) -> StreamResponse:
        return self.post("users/restore", data={"user_ids": user_ids})

    def deactivate_user(self, user_id: str, **options: Any) -> StreamResponse:
        return self.post(f"users/{user_id}/deactivate", data=options)

    def reactivate_user(self, user_id: str, **options: Any) -> StreamResponse:
        return self.post(f"users/{user_id}/reactivate", data=options)

    def export_user(self, user_id: str, **options: Any) -> StreamResponse:
        return self.get(f"users/{user_id}/export", options)

    def ban_user(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_user_id": target_id, **options}
        return self.post("moderation/ban", data=data)

    def shadow_ban(self, target_id: str, **options: Any) -> StreamResponse:
        return self.ban_user(target_id, shadow=True, **options)

    def remove_shadow_ban(self, target_id: str, **options: Any) -> StreamResponse:
        return self.unban_user(target_id, shadow=True, **options)

    def unban_user(self, target_id: str, **options: Any) -> StreamResponse:
        params = {"target_user_id": target_id, **options}
        return self.delete("moderation/ban", params)

    def query_banned_users(self, query_conditions: Dict) -> StreamResponse:
        return self.get(
            "query_banned_users", params={"payload": json.dumps(query_conditions)}
        )

    def run_message_action(self, message_id: str, data: Dict) -> StreamResponse:
        return self.post(f"messages/{message_id}/action", data=data)

    def flag_message(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_message_id": target_id, **options}
        return self.post("moderation/flag", data=data)

    def unflag_message(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_message_id": target_id, **options}
        return self.post("moderation/unflag", data=data)

    def query_message_flags(
        self, filter_conditions: Dict, **options: Any
    ) -> StreamResponse:
        params = {
            **options,
            "filter_conditions": filter_conditions,
        }
        return self.get(
            "moderation/flags/message", params={"payload": json.dumps(params)}
        )

    def flag_user(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_user_id": target_id, **options}
        return self.post("moderation/flag", data=data)

    def unflag_user(self, target_id: str, **options: Any) -> StreamResponse:
        data = {"target_user_id": target_id, **options}
        return self.post("moderation/unflag", data=data)

    def _query_flag_reports(self, **options: Any) -> StreamResponse:
        """
        Note: Do not use this.
        It is present for internal usage only.
        This function can, and will, break and/or be removed at any point in time.
        """
        data = {"filter_conditions": options}
        return self.post("moderation/reports", data=data)

    def _review_flag_report(
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
        return self.patch(f"moderation/reports/{report_id}", data=data)

    def mute_user(self, target_id: str, user_id: str, **options: Any) -> StreamResponse:
        data = {"target_id": target_id, "user_id": user_id, **options}
        return self.post("moderation/mute", data=data)

    def mute_users(
        self, target_ids: List[str], user_id: str, **options: Any
    ) -> StreamResponse:
        data = {"target_ids": target_ids, "user_id": user_id, **options}
        return self.post("moderation/mute", data=data)

    def unmute_user(self, target_id: str, user_id: str) -> StreamResponse:
        data = {"target_id": target_id, "user_id": user_id}
        return self.post("moderation/unmute", data=data)

    def unmute_users(self, target_ids: List[str], user_id: str) -> StreamResponse:
        data = {"target_ids": target_ids, "user_id": user_id}
        return self.post("moderation/unmute", data=data)

    def mark_all_read(self, user_id: str) -> StreamResponse:
        return self.post("channels/read", data={"user": {"id": user_id}})

    def translate_message(self, message_id: str, language: str) -> StreamResponse:
        return self.post(
            f"messages/{message_id}/translate", data={"language": language}
        )

    def commit_message(self, message_id: str) -> StreamResponse:
        return self.post(f"messages/{message_id}/commit")

    def pin_message(
        self, message_id: str, user_id: str, expiration: int = None
    ) -> StreamResponse:
        updates = {
            "set": {
                "pinned": True,
                "pin_expires": expiration,
            }
        }
        return self.update_message_partial(message_id, updates, user_id)

    def unpin_message(self, message_id: str, user_id: str) -> StreamResponse:
        updates = {
            "set": {
                "pinned": False,
            }
        }
        return self.update_message_partial(message_id, updates, user_id)

    def update_message(self, message: Dict) -> StreamResponse:
        if message.get("id") is None:
            raise ValueError("message must have an id")
        return self.post(f"messages/{message['id']}", data={"message": message})

    def update_message_partial(
        self, message_id: str, updates: Dict, user_id: str, **options: Any
    ) -> StreamResponse:
        data = updates.copy()
        if user_id:
            data["user"] = {"id": user_id}
        data.update(options)
        return self.put(f"messages/{message_id}", data=data)

    def delete_message(self, message_id: str, **options: Any) -> StreamResponse:
        return self.delete(f"messages/{message_id}", options)

    def get_message(self, message_id: str) -> StreamResponse:
        return self.get(f"messages/{message_id}")

    def query_users(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> StreamResponse:
        params: Dict = options.copy()
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return self.get("users", params={"payload": json.dumps(params)})

    def query_channels(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> StreamResponse:
        params: Dict[str, Any] = {"state": True, "watch": False, "presence": False}
        params.update(options)
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return self.post("channels", data=params)

    def create_channel_type(self, data: Dict) -> StreamResponse:
        if "commands" not in data or not data["commands"]:
            data["commands"] = ["all"]
        return self.post("channeltypes", data=data)

    def get_channel_type(self, channel_type: str) -> StreamResponse:
        return self.get(f"channeltypes/{channel_type}")

    def list_channel_types(self) -> StreamResponse:
        return self.get("channeltypes")

    def update_channel_type(self, channel_type: str, **settings: Any) -> StreamResponse:
        return self.put(f"channeltypes/{channel_type}", data=settings)

    def delete_channel_type(self, channel_type: str) -> StreamResponse:
        return self.delete(f"channeltypes/{channel_type}")

    def channel(  # type: ignore
        self, channel_type: str, channel_id: str = None, data: Dict = None
    ) -> Channel:
        return Channel(self, channel_type, channel_id, data)

    def delete_channels(self, cids: Iterable[str], **options: Any) -> StreamResponse:
        return self.post("channels/delete", data=dict(options, cids=cids))

    def list_commands(self) -> StreamResponse:
        return self.get("commands")

    def create_command(self, data: Dict) -> StreamResponse:
        return self.post("commands", data=data)

    def delete_command(self, name: str) -> StreamResponse:
        return self.delete(f"commands/{name}")

    def get_command(self, name: str) -> StreamResponse:
        return self.get(f"commands/{name}")

    def update_command(self, name: str, **settings: Any) -> StreamResponse:
        return self.put(f"commands/{name}", data=settings)

    def add_device(
        self,
        device_id: str,
        push_provider: str,
        user_id: str,
        push_provider_name: str = None,
    ) -> StreamResponse:
        return self.post(
            "devices",
            data={
                "id": device_id,
                "push_provider": push_provider,
                "user_id": user_id,
                "push_provider_name": push_provider_name,
            },
        )

    def delete_device(self, device_id: str, user_id: str) -> StreamResponse:
        return self.delete("devices", {"id": device_id, "user_id": user_id})

    def get_devices(self, user_id: str) -> StreamResponse:
        return self.get("devices", {"user_id": user_id})

    def get_rate_limits(
        self,
        server_side: bool = False,
        android: bool = False,
        ios: bool = False,
        web: bool = False,
        endpoints: Iterable[str] = None,
    ) -> StreamResponse:
        params: Dict[str, Any] = {}
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

        return self.get("rate_limits", params)

    def search(
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
        return self.get("search", params={"payload": json.dumps(params)})

    def send_file(
        self, uri: str, url: str, name: str, user: Dict, content_type: str = None
    ) -> StreamResponse:
        headers = {
            "Authorization": self.auth_token,
            "stream-auth-type": "jwt",
            "X-Stream-Client": get_user_agent(),
        }
        parts = urlparse(url)
        if parts[0] == "":
            with open(url, "rb") as f:
                content = f.read()
        else:
            content = urlopen(
                Request(url, headers={"User-Agent": "Mozilla/5.0"})
            ).read()
        response = requests.post(
            f"{self.base_url}/{uri}",
            params=self.get_default_params(),
            data={"user": json.dumps(user)},
            files={"file": (name, content, content_type)},  # type: ignore
            headers=headers,
        )
        return self._parse_response(response)

    def create_blocklist(
        self, name: str, words: Iterable[str], type: str = "regular"
    ) -> StreamResponse:
        return self.post(
            "blocklists", data={"name": name, "words": words, "type": type}
        )

    def list_blocklists(self) -> StreamResponse:
        return self.get("blocklists")

    def get_blocklist(self, name: str) -> StreamResponse:
        return self.get(f"blocklists/{name}")

    def update_blocklist(self, name: str, words: Iterable[str]) -> StreamResponse:
        return self.put(f"blocklists/{name}", data={"words": words})

    def delete_blocklist(self, name: str) -> StreamResponse:
        return self.delete(f"blocklists/{name}")

    def check_push(self, push_data: Dict) -> StreamResponse:
        return self.post("check_push", data=push_data)

    def check_sqs(
        self, sqs_key: str = None, sqs_secret: str = None, sqs_url: str = None
    ) -> StreamResponse:
        data = {"sqs_key": sqs_key, "sqs_secret": sqs_secret, "sqs_url": sqs_url}
        return self.post("check_sqs", data=data)

    def check_sns(
        self, sns_key: str = None, sns_secret: str = None, sns_topic_arn: str = None
    ) -> StreamResponse:
        data = {
            "sns_key": sns_key,
            "sns_secret": sns_secret,
            "sns_topic_arn": sns_topic_arn,
        }
        return self.post("check_sns", data=data)

    def get_permission(self, id: str) -> StreamResponse:
        return self.get(f"permissions/{id}")

    def create_permission(self, permission: Dict) -> StreamResponse:
        return self.post("permissions", data=permission)

    def update_permission(self, id: str, permission: Dict) -> StreamResponse:
        return self.put(f"permissions/{id}", data=permission)

    def delete_permission(self, id: str) -> StreamResponse:
        return self.delete(f"permissions/{id}")

    def list_permissions(self) -> StreamResponse:
        return self.get("permissions")

    def create_role(self, name: str) -> StreamResponse:
        return self.post("roles", data={"name": name})

    def delete_role(self, name: str) -> StreamResponse:
        return self.delete(f"roles/{name}")

    def list_roles(self) -> StreamResponse:
        return self.get("roles")

    def create_segment(self, segment: Dict) -> StreamResponse:
        return self.post("segments", data={"segment": segment})

    def query_segments(self, **params: Any) -> StreamResponse:
        return self.get("segments", params={"payload": json.dumps(params)})

    def update_segment(self, segment_id: str, data: Dict) -> StreamResponse:
        return self.put(f"segments/{segment_id}", data={"segment": data})

    def delete_segment(self, segment_id: str) -> StreamResponse:
        return self.delete(f"segments/{segment_id}")

    def create_campaign(self, campaign: Dict) -> StreamResponse:
        return self.post("campaigns", data={"campaign": campaign})

    def query_campaigns(self, **params: Any) -> StreamResponse:
        return self.get("campaigns", params={"payload": json.dumps(params)})

    def update_campaign(self, campaign_id: str, data: Dict) -> StreamResponse:
        return self.put(f"campaigns/{campaign_id}", data={"campaign": data})

    def delete_campaign(self, campaign_id: str, **options: Any) -> StreamResponse:
        return self.delete(f"campaigns/{campaign_id}", params=options)

    def schedule_campaign(
        self, campaign_id: str, scheduled_for: int = None
    ) -> StreamResponse:
        return self.patch(
            f"campaigns/{campaign_id}/schedule", data={"scheduled_for": scheduled_for}
        )

    def stop_campaign(self, campaign_id: str) -> StreamResponse:
        return self.patch(f"campaigns/{campaign_id}/stop")

    def resume_campaign(self, campaign_id: str) -> StreamResponse:
        return self.patch(f"campaigns/{campaign_id}/resume")

    def test_campaign(self, campaign_id: str, users: Iterable[str]) -> StreamResponse:
        return self.post(f"campaigns/{campaign_id}/test", data={"users": users})

    def query_recipients(self, **params: Any) -> StreamResponse:
        return self.get("recipients", params={"payload": json.dumps(params)})

    def revoke_tokens(self, since: Union[str, datetime.datetime]) -> StreamResponse:
        if isinstance(since, datetime.datetime):
            since = since.isoformat()

        return self.update_app_settings(revoke_tokens_issued_before=since)

    def revoke_user_token(
        self, user_id: str, before: Union[str, datetime.datetime]
    ) -> StreamResponse:
        return self.revoke_users_token([user_id], before)

    def revoke_users_token(
        self, user_ids: Iterable[str], before: Union[str, datetime.datetime]
    ) -> StreamResponse:
        if isinstance(before, datetime.datetime):
            before = before.isoformat()

        updates = []
        for user_id in user_ids:
            updates.append(
                {"id": user_id, "set": {"revoke_tokens_issued_before": before}}
            )
        return self.update_users_partial(updates)

    def export_channel(
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

        return self.export_channels(
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

    def export_channels(
        self, channels: Iterable[Dict], **options: Any
    ) -> StreamResponse:
        return self.post("export_channels", data={"channels": channels, **options})

    def get_export_channel_status(self, task_id: str) -> StreamResponse:
        return self.get(f"export_channels/{task_id}")

    def get_task(self, task_id: str) -> StreamResponse:
        return self.get(f"tasks/{task_id}")

    def send_user_custom_event(self, user_id: str, event: Dict) -> StreamResponse:
        return self.post(f"users/{user_id}/event", data={"event": event})

    def upsert_push_provider(self, push_provider_config: Dict) -> StreamResponse:
        return self.post("push_providers", data={"push_provider": push_provider_config})

    def delete_push_provider(self, provider_type: str, name: str) -> StreamResponse:
        return self.delete(f"push_providers/{provider_type}/{name}")

    def list_push_providers(self) -> StreamResponse:
        return self.get("push_providers")

    def create_import_url(self, filename: str) -> StreamResponse:
        return self.post("import_urls", data={"filename": filename})

    def create_import(
        self, path: str, mode: Literal["insert", "upsert"] = "upsert"
    ) -> StreamResponse:
        return self.post("imports", data={"path": path, "mode": mode})

    def get_import(self, id: str) -> StreamResponse:
        return self.get(f"imports/{id}")

    def list_imports(self, options: Dict = None) -> StreamResponse:
        return self.get("imports", params=options)
