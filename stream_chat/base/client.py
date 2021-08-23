import abc
import collections
import hashlib
import hmac

import jwt


class StreamChatInterface(abc.ABC):
    session = None

    @abc.abstractmethod
    def __init__(self, api_key, api_secret, timeout=6.0, **options):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.options = options
        self.base_url = options.get("base_url", "https://chat.stream-io-api.com")
        self.auth_token = jwt.encode(
            {"server": True}, self.api_secret, algorithm="HS256"
        )

    def get_default_params(self):
        return {"api_key": self.api_key}

    def normalize_sort(self, sort=None):
        sort_fields = []
        if isinstance(sort, collections.abc.Mapping):
            sort = [sort]
        if isinstance(sort, list):
            for item in sort:
                if "field" in item and "direction" in item:
                    sort_fields.append(item)
                else:
                    for k, v in item.items():
                        sort_fields.append({"field": k, "direction": v})
        return sort_fields

    def create_token(self, user_id, exp=None, iat=None, **claims):
        payload = {**claims, "user_id": user_id}
        if exp is not None:
            payload["exp"] = exp
        if iat is not None:
            payload["iat"] = iat
        return jwt.encode(payload, self.api_secret, algorithm="HS256")

    def create_search_params(self, filter_conditions, query, sort, **options):
        params = options.copy()
        if isinstance(query, str):
            params.update({"query": query})
        else:
            params.update({"message_filter_conditions": query})
        params.update(
            {"filter_conditions": filter_conditions, "sort": self.normalize_sort(sort)}
        )
        return params

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

    @abc.abstractmethod
    def update_app_settings(self, **settings):
        pass

    @abc.abstractmethod
    def get_app_settings(self):
        pass

    @abc.abstractmethod
    def update_users(self, users):
        pass

    @abc.abstractmethod
    def update_user(self, user):
        pass

    @abc.abstractmethod
    def update_users_partial(self, updates):
        pass

    @abc.abstractmethod
    def update_user_partial(self, update):
        pass

    @abc.abstractmethod
    def delete_user(self, user_id, **options):
        pass

    @abc.abstractmethod
    def deactivate_user(self, user_id, **options):
        pass

    @abc.abstractmethod
    def reactivate_user(self, user_id, **options):
        pass

    @abc.abstractmethod
    def export_user(self, user_id, **options):
        pass

    @abc.abstractmethod
    def ban_user(self, target_id, **options):
        pass

    @abc.abstractmethod
    def unban_user(self, target_id, **options):
        pass

    @abc.abstractmethod
    def flag_message(self, target_id, **options):
        pass

    @abc.abstractmethod
    def unflag_message(self, target_id, **options):
        pass

    @abc.abstractmethod
    def query_message_flags(self, filter_conditions, **options):
        pass

    @abc.abstractmethod
    def flag_user(self, target_id, **options):
        pass

    @abc.abstractmethod
    def unflag_user(self, target_id, **options):
        pass

    @abc.abstractmethod
    def mute_user(self, target_id, user_id, **options):
        """
        Create a mute

        :param target_id: the user getting muted
        :param user_id: the user muting the target
        :param options: additional mute options
        :return:
        """
        pass

    @abc.abstractmethod
    def unmute_user(self, target_id, user_id):
        """
        Removes a mute

        :param target_id: the user getting un-muted
        :param user_id: the user muting the target
        :return:
        """

        pass

    @abc.abstractmethod
    def mark_all_read(self, user_id):
        pass

    @abc.abstractmethod
    def update_message(self, message):
        pass

    @abc.abstractmethod
    def delete_message(self, message_id, **options):
        pass

    @abc.abstractmethod
    def get_message(self, message_id):
        pass

    @abc.abstractmethod
    def query_users(self, filter_conditions, sort=None, **options):
        pass

    @abc.abstractmethod
    def query_channels(self, filter_conditions, sort=None, **options):
        pass

    @abc.abstractmethod
    def create_channel_type(self, data):
        pass

    @abc.abstractmethod
    def get_channel_type(self, channel_type):
        pass

    @abc.abstractmethod
    def list_channel_types(self):
        pass

    @abc.abstractmethod
    def update_channel_type(self, channel_type, **settings):
        pass

    @abc.abstractmethod
    def delete_channel_type(self, channel_type):
        """
        Delete a type of channel

        :param channel_type: the channel type
        :return:
        """
        pass

    @abc.abstractmethod
    def channel(self, channel_type, channel_id=None, data=None):
        """
        Creates a channel object

        :param channel_type: the channel type
        :param channel_id: the id of the channel
        :param data: additional data, ie: {"members":[id1, id2, ...]}
        :return: Channel
        """
        pass

    @abc.abstractmethod
    def list_commands(self):
        pass

    @abc.abstractmethod
    def create_command(self, data):
        pass

    @abc.abstractmethod
    def delete_command(self, name):
        pass

    @abc.abstractmethod
    def get_command(self, name):
        pass

    @abc.abstractmethod
    def update_command(self, name, **settings):
        pass

    @abc.abstractmethod
    def add_device(self, device_id, push_provider, user_id):
        """
        Add a device to a user

        :param device_id: the id of the device
        :param push_provider: the push provider used (apn or firebase)
        :param user_id: the id of the user
        :return:
        """
        pass

    @abc.abstractmethod
    def delete_device(self, device_id, user_id):
        """
        Delete a device for a user

        :param device_id: the id of the device
        :param user_id: the id of the user
        :return:
        """
        pass

    @abc.abstractmethod
    def get_devices(self, user_id):
        """
        Get the list of devices for a user

        :param user_id: the id of the user
        :return: list of devices
        """
        pass

    @abc.abstractmethod
    def get_rate_limits(self, server_side, android, ios, web, endpoints):
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
    def search(self, filter_conditions, query, **options):
        pass

    @abc.abstractmethod
    def send_file(self, uri, url, name, user, content_type=None):
        pass

    @abc.abstractmethod
    def create_blocklist(self, name, words):
        """
        Create a blocklist

        :param name: the name of the blocklist
        :param words: list of blocked words
        :return:
        """
        pass

    @abc.abstractmethod
    def list_blocklists(self):
        """
        List blocklists

        :return: list of blocklists
        """
        pass

    @abc.abstractmethod
    def get_blocklist(self, name):
        """Get a blocklist by name

        :param name: the name of the blocklist
        :return: blocklist dict representation
        """
        pass

    @abc.abstractmethod
    def update_blocklist(self, name, words):
        """
        Update a blocklist

        :param name: the name of the blocklist
        :param words: the list of blocked words (replaces the current list)
        :return:
        """
        pass

    @abc.abstractmethod
    def delete_blocklist(self, name):
        """Delete a blocklist by name

        :param: the name of the blocklist
        :return:
        """
        pass

    @abc.abstractmethod
    def check_sqs(self, sqs_key=None, sqs_secret=None, sqs_url=None):
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
    def get_permission(self, name):
        """
        Get the definition for a permission

        :param name: Name of the permission
        """
        pass

    @abc.abstractmethod
    def create_permission(self, permission):
        """
        Create a custom permission

        :param permission: Definition of the permission
        """
        pass

    @abc.abstractmethod
    def update_permission(self, name, permission):
        """
        Update a custom permission

        :param name: Name of the permission
        :param permission: New definition of the permission
        """
        pass

    @abc.abstractmethod
    def delete_permission(self, name):
        """
        Delete a custom permission

        :param name: Name of the permission
        """
        pass

    @abc.abstractmethod
    def list_permissions(self):
        """
        List all permissions of the app
        """
        pass

    @abc.abstractmethod
    def create_role(self, name):
        """
        Create a custom role

        :param name: Name of the role
        """
        pass

    @abc.abstractmethod
    def delete_role(self, name):
        """
        Delete a custom role

        :param name: Name of the role
        """
        pass

    @abc.abstractmethod
    def list_roles(self):
        """
        List all roles of the app
        """
        pass

    @abc.abstractmethod
    def create_segment(self, segment):
        """
        Create a segment
        """
        pass

    @abc.abstractmethod
    def get_segment(self, segment_id):
        """
        Get a segment by id
        """
        pass

    @abc.abstractmethod
    def list_segments(self, **params):
        """
        List segments
        """
        pass

    @abc.abstractmethod
    def update_segment(self, segment_id, data):
        """
        Update a segment by id
        """
        pass

    @abc.abstractmethod
    def delete_segment(self, segment_id):
        """
        Delete a segment by id
        """
        pass

    @abc.abstractmethod
    def create_campaign(self, campaign):
        """
        Create a campaign
        """
        pass

    @abc.abstractmethod
    def get_campaign(self, campaign_id):
        """
        Get a campaign by id
        """
        pass

    @abc.abstractmethod
    def list_campaigns(self, **params):
        """
        List campaigns
        """
        pass

    @abc.abstractmethod
    def update_campaign(self, campaign_id, data):
        """
        Update a campaign
        """
        pass

    @abc.abstractmethod
    def delete_campaign(self, campaign_id):
        """
        Delete a campaign by id
        """
        pass

    @abc.abstractmethod
    def schedule_campaign(self, campaign_id, send_at=None):
        """
        Schedule a campaign at given time
        """
        pass

    @abc.abstractmethod
    async def stop_campaign(self, campaign_id):
        """
        Stop a in progress campaign
        """
        pass

    @abc.abstractmethod
    def resume_campaign(self, campaign_id):
        """
        Resume a stopped campaign
        """
        pass

    @abc.abstractmethod
    def test_campaign(self, campaign_id, users):
        """
        Trigger a test send of the given campaing to given users
        """
        pass

    @abc.abstractmethod
    def revoke_tokens(self, since):
        """
        Revoke tokens for an application issued since
        """
        pass

    @abc.abstractmethod
    def revoke_user_token(self, user_id, since):
        """
        Revoke tokens for a user issued since
        """
        pass

    @abc.abstractmethod
    def revoke_users_token(self, user_ids, since):
        """
        Revoke tokens for users issued since
        """
        pass

    @abc.abstractmethod
    def export_channel(
        self, channel_type, channel_id, messages_since=None, messages_until=None
    ):
        """
        Requests a channel export
        """
        pass

    @abc.abstractmethod
    def export_channels(self, channels):
        """
        Requests a channels export
        """
        pass

    @abc.abstractmethod
    def get_export_channel_status(self, task_id):
        """
        Retrieves status of export
        """
        pass
