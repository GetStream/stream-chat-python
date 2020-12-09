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
        self.base_url = options.get(
            "base_url", "https://chat-us-east-1.stream-io-api.com"
        )
        self.auth_token = jwt.encode(
            {"server": True}, self.api_secret, algorithm="HS256"
        ).decode()

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

    def create_token(self, user_id, exp=None):
        payload = {"user_id": user_id}
        if exp is not None:
            payload["exp"] = exp
        return jwt.encode(payload, self.api_secret, algorithm="HS256").decode()

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
