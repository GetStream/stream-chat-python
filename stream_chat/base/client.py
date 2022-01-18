import abc
import collections
import datetime
import hashlib
import hmac
from typing import Any, Awaitable, Dict, Iterable, List, TypeVar, Union

import jwt

from stream_chat.types.stream_response import StreamResponse

TChannel = TypeVar("TChannel")


class StreamChatInterface(abc.ABC):
    def __init__(
        self, api_key: str, api_secret: str, timeout: float = 6.0, **options: Any
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.options = options
        self.base_url = options.get("base_url", "https://chat.stream-io-api.com")
        self.auth_token = jwt.encode(
            {"server": True}, self.api_secret, algorithm="HS256"
        )

    def get_default_params(self) -> Dict[str, str]:
        return {"api_key": self.api_key}

    def normalize_sort(self, sort: Union[Dict, List[Dict]] = None) -> List[Dict]:
        sort_fields = []
        if isinstance(sort, collections.abc.Mapping):
            sort = [sort]  # type: ignore
        if isinstance(sort, list):
            for item in sort:
                if "field" in item and "direction" in item:
                    sort_fields.append(item)
                else:
                    for k, v in item.items():
                        sort_fields.append({"field": k, "direction": v})
        return sort_fields

    def create_token(
        self, user_id: str, exp: int = None, iat: int = None, **claims: Any
    ) -> str:
        payload: Dict[str, Any] = {**claims, "user_id": user_id}
        if exp:
            payload["exp"] = exp
        if iat:
            payload["iat"] = iat
        return jwt.encode(payload, self.api_secret, algorithm="HS256")

    def create_search_params(
        self,
        filter_conditions: Dict,
        query: Union[str, Dict],
        sort: List[Dict] = None,
        **options: Any,
    ) -> Dict[str, Any]:
        params = options.copy()
        if isinstance(query, str):
            params.update({"query": query})
        else:
            params.update({"message_filter_conditions": query})

        params.update({"filter_conditions": filter_conditions})
        if sort:
            params.update({"sort": self.normalize_sort(sort)})

        return params

    def verify_webhook(self, request_body: bytes, x_signature: str) -> bool:
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

    @abc.abstractmethod
    def update_app_settings(
        self, **settings: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def get_app_settings(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_users(
        self, users: List[Dict]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_user(
        self, user: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_users_partial(
        self, updates: List[Dict]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_user_partial(
        self, update: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete_users(
        self, user_ids: Iterable[str], delete_type: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete users asynchronously

        :param user_ids: a list of user IDs to delete
        :param delete_type: type of user delete (hard|soft)
        :param options: additional delete options
        :return: task_id
        """
        pass

    @abc.abstractmethod
    def deactivate_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def reactivate_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def export_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def ban_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def shadow_ban(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def remove_shadow_ban(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def unban_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def flag_message(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def unflag_message(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def query_message_flags(
        self, filter_conditions: Dict, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def flag_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def unflag_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def mute_user(
        self, target_id: str, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a mute

        :param target_id: the user getting muted
        :param user_id: the user muting the target
        :param options: additional mute options
        :return:
        """
        pass

    @abc.abstractmethod
    def unmute_user(
        self, target_id: str, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Removes a mute

        :param target_id: the user getting un-muted
        :param user_id: the user muting the target
        :return:
        """

        pass

    @abc.abstractmethod
    def mark_all_read(
        self, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def pin_message(
        self, message_id: str, user_id: str, expiration: int = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def unpin_message(
        self, message_id: str, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_message(
        self, message: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_message_partial(
        self, message_id: str, updates: Dict, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete_message(
        self, message_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def get_message(
        self, message_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def query_users(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def query_channels(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def create_channel_type(
        self, data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def get_channel_type(
        self, channel_type: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def list_channel_types(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_channel_type(
        self, channel_type: str, **settings: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete_channel_type(
        self, channel_type: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a type of channel

        :param channel_type: the channel type
        :return:
        """
        pass

    @abc.abstractmethod
    def channel(
        self, channel_type: str, channel_id: str = None, data: Dict = None
    ) -> TChannel:
        """
        Creates a channel object

        :param channel_type: the channel type
        :param channel_id: the id of the channel
        :param data: additional data, ie: {"members":[id1, id2, ...]}
        :return: Channel
        """
        pass

    @abc.abstractmethod
    def delete_channels(
        self, cids: Iterable[str], **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def list_commands(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def create_command(
        self, data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete_command(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def get_command(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update_command(
        self, name: str, **settings: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def add_device(
        self, device_id: str, push_provider: str, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Add a device to a user

        :param device_id: the id of the device
        :param push_provider: the push provider used (apn or firebase)
        :param user_id: the id of the user
        :return:
        """
        pass

    @abc.abstractmethod
    def delete_device(
        self, device_id: str, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a device for a user

        :param device_id: the id of the device
        :param user_id: the id of the user
        :return:
        """
        pass

    @abc.abstractmethod
    def get_devices(
        self, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get the list of devices for a user

        :param user_id: the id of the user
        :return: list of devices
        """
        pass

    @abc.abstractmethod
    def get_rate_limits(
        self,
        server_side: bool = False,
        android: bool = False,
        ios: bool = False,
        web: bool = False,
        endpoints: Iterable[str] = None,
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get rate limit quotas and usage.
        If no params are toggled, all limits for all endpoints are returned.

        :param server_side: if true, show server_side limits.
        :param android: if true, show android limits.
        :param ios: if true, show ios limits.
        :param web: if true, show web limits.
        :param endpoints: restrict returned limits to the given list of endpoints.
        """
        pass

    @abc.abstractmethod
    def search(
        self,
        filter_conditions: Dict,
        query: Union[str, Dict],
        sort: List[Dict] = None,
        **options: Any,
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def send_file(
        self, uri: str, url: str, name: str, user: Dict, content_type: str = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def create_blocklist(
        self, name: str, words: Iterable[str]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a blocklist

        :param name: the name of the blocklist
        :param words: list of blocked words
        :return:
        """
        pass

    @abc.abstractmethod
    def list_blocklists(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List blocklists

        :return: list of blocklists
        """
        pass

    @abc.abstractmethod
    def get_blocklist(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """Get a blocklist by name

        :param name: the name of the blocklist
        :return: blocklist dict representation
        """
        pass

    @abc.abstractmethod
    def update_blocklist(
        self, name: str, words: Iterable[str]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Update a blocklist

        :param name: the name of the blocklist
        :param words: the list of blocked words (replaces the current list)
        :return:
        """
        pass

    @abc.abstractmethod
    def delete_blocklist(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """Delete a blocklist by name

        :param: the name of the blocklist
        :return:
        """
        pass

    @abc.abstractmethod
    def check_sqs(
        self, sqs_key: str = None, sqs_secret: str = None, sqs_url: str = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Check SQS Push settings

        When no parameters are given, the current SQS app settings are used

        :param sqs_key: AWS access key
        :param sqs_secret: AWS secret key
        :param sqs_url: URL to SQS queue
        :return:
        """
        pass

    @abc.abstractmethod
    def get_permission(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get the definition for a permission

        :param name: Name of the permission
        """
        pass

    @abc.abstractmethod
    def create_permission(
        self, permission: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a custom permission

        :param permission: Definition of the permission
        """
        pass

    @abc.abstractmethod
    def update_permission(
        self, name: str, permission: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Update a custom permission

        :param name: Name of the permission
        :param permission: New definition of the permission
        """
        pass

    @abc.abstractmethod
    def delete_permission(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a custom permission

        :param name: Name of the permission
        """
        pass

    @abc.abstractmethod
    def list_permissions(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List all permissions of the app
        """
        pass

    @abc.abstractmethod
    def create_role(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a custom role

        :param name: Name of the role
        """
        pass

    @abc.abstractmethod
    def delete_role(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a custom role

        :param name: Name of the role
        """
        pass

    @abc.abstractmethod
    def list_roles(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List all roles of the app
        """
        pass

    @abc.abstractmethod
    def create_segment(
        self, segment: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a segment
        """
        pass

    @abc.abstractmethod
    def get_segment(
        self, segment_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get a segment by id
        """
        pass

    @abc.abstractmethod
    def list_segments(
        self, **params: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List segments
        """
        pass

    @abc.abstractmethod
    def update_segment(
        self, segment_id: str, data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Update a segment by id
        """
        pass

    @abc.abstractmethod
    def delete_segment(
        self, segment_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a segment by id
        """
        pass

    @abc.abstractmethod
    def create_campaign(
        self, campaign: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a campaign
        """
        pass

    @abc.abstractmethod
    def get_campaign(
        self, campaign_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get a campaign by id
        """
        pass

    @abc.abstractmethod
    def list_campaigns(
        self, **params: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List campaigns
        """
        pass

    @abc.abstractmethod
    def update_campaign(
        self, campaign_id: str, data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Update a campaign
        """
        pass

    @abc.abstractmethod
    def delete_campaign(
        self, campaign_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a campaign by id
        """
        pass

    @abc.abstractmethod
    def schedule_campaign(
        self, campaign_id: str, send_at: int = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Schedule a campaign at given time
        """
        pass

    @abc.abstractmethod
    def stop_campaign(
        self, campaign_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Stop a in progress campaign
        """
        pass

    @abc.abstractmethod
    def resume_campaign(
        self, campaign_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Resume a stopped campaign
        """
        pass

    @abc.abstractmethod
    def test_campaign(
        self, campaign_id: str, users: Iterable[str]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Trigger a test send of the given campaing to given users
        """
        pass

    @abc.abstractmethod
    def revoke_tokens(
        self, since: Union[str, datetime.datetime]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Revoke tokens for an application issued since
        """
        pass

    @abc.abstractmethod
    def revoke_user_token(
        self, user_id: str, before: Union[str, datetime.datetime]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Revoke tokens for a user issued since
        """
        pass

    @abc.abstractmethod
    def revoke_users_token(
        self, user_ids: Iterable[str], before: Union[str, datetime.datetime]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Revoke tokens for users issued since
        """
        pass

    @abc.abstractmethod
    def export_channel(
        self,
        channel_type: str,
        channel_id: str,
        messages_since: Union[str, datetime.datetime] = None,
        messages_until: Union[str, datetime.datetime] = None,
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Requests a channel export
        """
        pass

    @abc.abstractmethod
    def export_channels(
        self, channels: Iterable[Dict]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Requests a channels export
        """
        pass

    @abc.abstractmethod
    def get_export_channel_status(
        self, task_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Retrieves status of export
        """
        pass

    @abc.abstractmethod
    def get_task(
        self, task_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Retrieves status of task
        """
        pass

    #####################
    #  Private methods  #
    #####################

    @abc.abstractmethod
    def get(self, relative_url: str, params: Dict = None) -> Any:
        pass

    @abc.abstractmethod
    def post(self, relative_url: str, params: Dict = None, data: Any = None) -> Any:
        pass

    @abc.abstractmethod
    def delete(self, relative_url: str, params: Dict = None) -> Any:
        pass

    @abc.abstractmethod
    def patch(self, relative_url: str, params: Dict = None, data: Any = None) -> Any:
        pass

    @abc.abstractmethod
    def put(self, relative_url: str, params: Dict = None, data: Any = None) -> Any:
        pass
