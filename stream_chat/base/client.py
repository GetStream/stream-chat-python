import abc
import collections
import datetime
import hashlib
import hmac
import os
import sys
from typing import Any, Awaitable, Dict, Iterable, List, TypeVar, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

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

        if os.getenv("STREAM_CHAT_TIMEOUT"):
            self.timeout = float(os.environ["STREAM_CHAT_TIMEOUT"])

        self.options = options
        self.base_url = "https://chat.stream-io-api.com"

        if options.get("base_url"):
            self.base_url = options["base_url"]
        elif os.getenv("STREAM_CHAT_URL"):
            self.base_url = os.environ["STREAM_CHAT_URL"]

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
        """
        Creates a JWT for a user.
        Stream uses JWT (JSON Web Tokens) to authenticate chat users, enabling them to login.
        Knowing whether a user is authorized to perform certain actions is managed
        separately via a role based permissions system.
        By default, user tokens are valid indefinitely. You can set an `exp`
        or issued at (`iat`) claim as well.
        """
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

    def verify_webhook(
        self, request_body: bytes, x_signature: Union[str, bytes]
    ) -> bool:
        """
        Verify the signature added to a webhook event

        :param request_body: the request body received from webhook
        :param x_signature: the x-signature header included in the request
        :return: bool
        """
        if isinstance(x_signature, bytes):
            x_signature = x_signature.decode()

        signature = hmac.new(
            key=self.api_secret.encode(), msg=request_body, digestmod=hashlib.sha256
        ).hexdigest()
        return signature == x_signature

    @abc.abstractmethod
    def update_app_settings(
        self, **settings: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Update the app settings.
        """
        pass

    @abc.abstractmethod
    def get_app_settings(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get the app settings.
        """
        pass

    @abc.abstractmethod
    def set_guest_user(
        self, guest_user: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Sets up a new guest user

        :param guest_user: the guest user data
        :return:
        """
        pass

    @abc.abstractmethod
    def update_users(
        self, users: List[Dict]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        DEPRECATED: Use upsert_users instead.
        """
        pass

    @abc.abstractmethod
    def update_user(
        self, user: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        DEPRECATED: Use upsert_user instead.
        """
        pass

    @abc.abstractmethod
    def upsert_users(
        self, users: List[Dict]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Creates new or updates existing users.
        """
        pass

    @abc.abstractmethod
    def upsert_user(
        self, user: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Creates a new or updates an existing user.
        """
        pass

    @abc.abstractmethod
    def update_users_partial(
        self, updates: List[Dict]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Updates multiple users partially.
        """
        pass

    @abc.abstractmethod
    def update_user_partial(
        self, update: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Updates a user partially.
        """
        pass

    @abc.abstractmethod
    def delete_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Deletes a user synchronously. Use delete_users for batch delete.
        """
        pass

    @abc.abstractmethod
    def delete_users(
        self, user_ids: Iterable[str], delete_type: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete users asynchronously. Use `get_task` to check the status of the task.

        :param user_ids: a list of user IDs to delete
        :param delete_type: type of user delete (hard|soft)
        :param options: additional delete options
        :return: task_id
        """
        pass

    @abc.abstractmethod
    def restore_users(
        self, user_ids: Iterable[str]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Restores soft deleted users.
        """
        pass

    @abc.abstractmethod
    def deactivate_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Deactivates a user.
        Deactivated users cannot connect to Stream Chat, and can't send or receive messages.
        To reactivate a user, use `reactivate_user` method.
        """
        pass

    @abc.abstractmethod
    def reactivate_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Reactivates a deactivated user. Use `deactivate_user` to deactivate a user.
        """
        pass

    @abc.abstractmethod
    def export_user(
        self, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Exports a user. It exports a user and returns an object
        containing all of it's data.
        """
        pass

    @abc.abstractmethod
    def ban_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Bans a user. Users can be banned from an app entirely or from a channel.
        When a user is banned, they will not be allowed to post messages until the
        ban is removed or expired but will be able to connect to Chat and to channels as before.
        To unban a user, use `unban_user` method.
        """
        pass

    @abc.abstractmethod
    def shadow_ban(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Shadow ban a user.
        When a user is shadow banned, they will still be allowed to post messages,
        but any message sent during the will only be visible to the messages author
        and invisible to other users of the App.
        To remove a shadow ban, use `remove_shadow_ban` method.
        """
        pass

    @abc.abstractmethod
    def remove_shadow_ban(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Removes a shadow ban of a user.
        When a user is shadow banned, they will still be allowed to post messages,
        but any message sent during the will only be visible to the messages author
        and invisible to other users of the App.
        To shadow ban a user, use `shadow_ban` method.
        """
        pass

    @abc.abstractmethod
    def unban_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Unbans a user. Users can be banned from an app entirely or from a channel.
        When a user is banned, they will not be allowed to post messages until the
        ban is removed or expired but will be able to connect to Chat and to channels as before.
        To ban a user, use `ban_user` method.
        """
        pass

    @abc.abstractmethod
    def query_banned_users(
        self, query_conditions: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Queries banned users.
        Banned users can be retrieved in different ways:
        1) Using the dedicated query bans endpoint
        2) User Search: you can add the banned:true condition to your search. Please note that
        this will only return users that were banned at the app-level and not the ones
        that were banned only on channels.
        """
        pass

    @abc.abstractmethod
    def run_message_action(
        self, message_id: str, data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Runs a message command action.
        """
        pass

    @abc.abstractmethod
    def flag_message(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Flags a message.
        Any user is allowed to flag a message. This triggers the message.flagged
        webhook event and adds the message to the inbox of your
        Stream Dashboard Chat Moderation view.
        """
        pass

    @abc.abstractmethod
    def unflag_message(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Unflags a message.
        Any user is allowed to flag a message. This triggers the message.flagged
        webhook event and adds the message to the inbox of your
        Stream Dashboard Chat Moderation view.
        """
        pass

    @abc.abstractmethod
    def query_message_flags(
        self, filter_conditions: Dict, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Queries message flags.
        If you prefer to build your own in app moderation dashboard, rather than use the Stream
        dashboard, then the query message flags endpoint lets you get flagged messages. Similar
        to other queries in Stream Chat, you can filter the flags using query operators.
        """
        pass

    @abc.abstractmethod
    def flag_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Flags a user.
        """
        pass

    @abc.abstractmethod
    def unflag_user(
        self, target_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Unflags a user.
        """
        pass

    @abc.abstractmethod
    def mute_users(
        self, target_ids: List[str], user_id: str, **options: Any
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
    def unmute_users(
        self, target_ids: List[str], user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def mark_all_read(
        self, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Marks all messages as read for a user.
        """
        pass

    @abc.abstractmethod
    def translate_message(
        self, message_id: str, language: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Translates a message

        :param message_id: Id of the message to be translated
        :param language: Target language of the translation
        :return:
        """
        pass

    @abc.abstractmethod
    def pin_message(
        self, message_id: str, user_id: str, expiration: int = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Pins a message.
        Pinned messages allow users to highlight important messages, make announcements, or temporarily
        promote content. Pinning a message is, by default, restricted to certain user roles,
        but this is flexible. Each channel can have multiple pinned messages and these can be created
        or updated with or without an expiration.
        """
        pass

    @abc.abstractmethod
    def unpin_message(
        self, message_id: str, user_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Unpins a message.
        Pinned messages allow users to highlight important messages, make announcements, or temporarily
        promote content. Pinning a message is, by default, restricted to certain user roles,
        but this is flexible. Each channel can have multiple pinned messages and these can be created
        or updated with or without an expiration.
        """
        pass

    @abc.abstractmethod
    def update_message(
        self, message: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Updates a message. Fully overwrites a message.
        For partial update, use `update_message_partial` method.
        """
        pass

    @abc.abstractmethod
    def update_message_partial(
        self, message_id: str, updates: Dict, user_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Updates a message partially.
        A partial update can be used to set and unset specific fields when
        it is necessary to retain additional data fields on the object. AKA a patch style update.
        """
        pass

    @abc.abstractmethod
    def delete_message(
        self, message_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Deletes a message.
        """
        pass

    @abc.abstractmethod
    def get_message(
        self, message_id: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Returns a single message.
        """
        pass

    @abc.abstractmethod
    def query_users(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Allows you to search for users and see if they are online/offline.
        You can filter and sort on the custom fields you've set for your user, the user id, and when the user was last active.
        """
        pass

    @abc.abstractmethod
    def query_channels(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Queries channels.
        You can query channels based on built-in fields as well as any custom field you add to channels.
        Multiple filters can be combined using AND, OR logical operators, each filter can use its
        comparison (equality, inequality, greater than, greater or equal, etc.).
        You can find the complete list of supported operators in the query syntax section of the docs.
        """
        pass

    @abc.abstractmethod
    def create_channel_type(
        self, data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Creates a channel type.
        """
        pass

    @abc.abstractmethod
    def get_channel_type(
        self, channel_type: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Returns a channel type.
        """
        pass

    @abc.abstractmethod
    def list_channel_types(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Returns a list of channel types.
        """
        pass

    @abc.abstractmethod
    def update_channel_type(
        self, channel_type: str, **settings: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Updates a channel type.
        """
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
    ) -> TChannel:  # type: ignore[type-var]
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
        """
        Deletes multiple channels. This is an asynchronous operation and the returned value is a task Id.
        You can use `get_task` method to check the status of the task.
        """
        pass

    @abc.abstractmethod
    def list_commands(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Returns a list of commands.
        By using custom commands, you can receive all messages sent using a specific slash command,
        eg. /ticket, in your application. When configured, every slash command message happening
        in a Stream Chat application will propagate to an endpoint via an HTTP POST request.
        """
        pass

    @abc.abstractmethod
    def create_command(
        self, data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Creates a command.
        By using custom commands, you can receive all messages sent using a specific slash command,
        eg. /ticket, in your application. When configured, every slash command message happening
        in a Stream Chat application will propagate to an endpoint via an HTTP POST request.
        """
        pass

    @abc.abstractmethod
    def delete_command(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Deletes a command.
        By using custom commands, you can receive all messages sent using a specific slash command,
        eg. /ticket, in your application. When configured, every slash command message happening
        in a Stream Chat application will propagate to an endpoint via an HTTP POST request.
        """
        pass

    @abc.abstractmethod
    def get_command(
        self, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Returns a command.
        By using custom commands, you can receive all messages sent using a specific slash command,
        eg. /ticket, in your application. When configured, every slash command message happening
        in a Stream Chat application will propagate to an endpoint via an HTTP POST request.
        """
        pass

    @abc.abstractmethod
    def update_command(
        self, name: str, **settings: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Updates a command.
        By using custom commands, you can receive all messages sent using a specific slash command,
        eg. /ticket, in your application. When configured, every slash command message happening
        in a Stream Chat application will propagate to an endpoint via an HTTP POST request.
        """
        pass

    @abc.abstractmethod
    def add_device(
        self,
        device_id: str,
        push_provider: str,
        user_id: str,
        push_provider_name: str = None,
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
        """
        Searches for messages.
        You can enable and/or disable the search indexing on a per channel
        type through the Stream Dashboard.
        """
        pass

    @abc.abstractmethod
    def send_file(
        self, uri: str, url: str, name: str, user: Dict, content_type: str = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Uploads a file.
        This functionality defaults to using the Stream CDN. If you would like, you can
        easily change the logic to upload to your own CDN of choice.
        """
        pass

    @abc.abstractmethod
    def create_blocklist(
        self, name: str, words: Iterable[str], type: str = "regular"
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a blocklist

        :param name: the name of the blocklist
        :param words: list of blocked words
        :param type: blocklist type
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
    def check_push(
        self, push_data: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Check push notification settings

        :param push_data: Test data for testing push notification settings
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
    def query_segments(
        self, **params: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Query segments
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
    def query_campaigns(
        self, **params: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Query campaigns
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
        self, campaign_id: str, **options: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a campaign by id
        """
        pass

    @abc.abstractmethod
    def schedule_campaign(
        self, campaign_id: str, scheduled_for: int = None
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
    def query_recipients(
        self, **params: Any
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Query recipients
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
        **options: Any,
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Requests a channel export.
        Channel exports are created asynchronously, you can use the Task ID returned by
        the APIs to keep track of the status and to download the final result when it is ready.
        Use `get_task` to check the status of the export.
        """
        pass

    @abc.abstractmethod
    def export_channels(
        self, channels: Iterable[Dict], **options: Any
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

    @abc.abstractmethod
    def send_user_custom_event(
        self, user_id: str, event: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Allows you to send custom events to a connected user.
        """
        pass

    @abc.abstractmethod
    def upsert_push_provider(
        self, push_provider_config: Dict
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create or update a push provider.
        """
        pass

    @abc.abstractmethod
    def delete_push_provider(
        self, provider_type: str, name: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Delete a push provider.
        """
        pass

    @abc.abstractmethod
    def list_push_providers(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get all push providers in the app.
        """
        pass

    @abc.abstractmethod
    def create_import_url(
        self, filename: str
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create a URL to import a file.
        Full flow:
        ::

            url_resp = client.create_import_url("myfile.json")

            upload_resp = requests.put(
                url_resp["upload_url"],
                data=open("myfile.json", "rb"),
                headers={"Content-Type": "application/json"},
            )

            create_resp = client.create_import(url_resp["path"], "upsert")
            import_resp = client.get_import(create_resp["import_task"]["id"])
        """
        pass

    @abc.abstractmethod
    def create_import(
        self, path: str, mode: Literal["insert", "upsert"] = "upsert"
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Create an import task.
        Full flow:
        ::

            url_resp = client.create_import_url("myfile.json")

            upload_resp = requests.put(
                url_resp["upload_url"],
                data=open("myfile.json", "rb"),
                headers={"Content-Type": "application/json"},
            )

            create_resp = client.create_import(url_resp["path"], "upsert")
            import_resp = client.get_import(create_resp["import_task"]["id"])
        """
        pass

    @abc.abstractmethod
    def get_import(self, id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        Get the status of an import task.
        Full flow:
        ::

            url_resp = client.create_import_url("myfile.json")

            upload_resp = requests.put(
                url_resp["upload_url"],
                data=open("myfile.json", "rb"),
                headers={"Content-Type": "application/json"},
            )

            create_resp = client.create_import(url_resp["path"], "upsert")
            import_resp = client.get_import(create_resp["import_task"]["id"])
        """
        pass

    @abc.abstractmethod
    def list_imports(
        self, options: Dict = None
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        """
        List all import tasks. Options can contain a "limit" and "offset" parameter.
        Full flow:
        ::

            url_resp = client.create_import_url("myfile.json")

            upload_resp = requests.put(
                url_resp["upload_url"],
                data=open("myfile.json", "rb"),
                headers={"Content-Type": "application/json"},
            )

            create_resp = client.create_import(url_resp["path"], "upsert")
            import_resp = client.get_import(create_resp["import_task"]["id"])
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
