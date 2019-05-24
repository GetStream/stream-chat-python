import jwt
import pytest
import uuid
from stream_chat import StreamChat
from stream_chat.exceptions import StreamAPIException


@pytest.mark.incremental
class TestClient(object):
    def test_mute_user(self, client, random_users):
        response = client.mute_user(random_users[0]["id"], random_users[1]["id"])
        assert "mute" in response
        assert response["mute"]["target"]["id"] == random_users[0]["id"]
        assert response["mute"]["user"]["id"] == random_users[1]["id"]
        client.unmute_user(random_users[0]["id"], random_users[1]["id"])

    def test_auth_exception(self):
        client = StreamChat(api_key="bad", api_secret="guy")
        with pytest.raises(StreamAPIException):
            client.get_channel_type("team")

    def test_get_channel_types(self, client):
        response = client.get_channel_type("team")
        assert "permissions" in response

    def test_list_channel_types(self, client):
        response = client.list_channel_types()
        assert "channel_types" in response

    def test_create_token(self, client):
        token = client.create_token("tommaso")
        payload = jwt.decode(token, client.api_secret, algorithm="HS256")
        assert payload.get("user_id") == "tommaso"

    def test_get_app_settings(self, client):
        configs = client.get_app_settings()
        assert "app" in configs

    def test_update_user(self, client):
        user = {"id": str(uuid.uuid4())}
        response = client.update_user(user)
        assert "users" in response
        assert user["id"] in response["users"]

    def test_update_users(self, client):
        user = {"id": str(uuid.uuid4())}
        response = client.update_users([user])
        assert "users" in response
        assert user["id"] in response["users"]

    def test_delete_user(self, client, random_user):
        response = client.delete_user(random_user["id"])
        assert "user" in response
        assert random_user["id"] == response["user"]["id"]

    def test_deactivate_user(self, client, random_user):
        response = client.deactivate_user(random_user["id"])
        assert "user" in response
        assert random_user["id"] == response["user"]["id"]

    def test_export_user(self, client, fellowship_of_the_ring):
        response = client.export_user("gandalf")
        assert "user" in response
        assert response["user"]["name"] == "Gandalf the Grey"

    def test_ban_user(self, client, random_user):
        client.ban_user(random_user["id"])

    def test_unban_user(self, client, random_user):
        client.ban_user(random_user["id"])
        client.unban_user(random_user["id"])

    def test_mark_all_read(self, client, random_user):
        client.mark_all_read(random_user["id"])

    def test_update_message(self, client, channel, random_user):
        msg_id = str(uuid.uuid4())
        response = channel.send_message(
            {"id": msg_id, "text": "hello world"}, random_user["id"]
        )
        assert response["message"]["text"] == "hello world"
        client.update_message(
            {
                "id": msg_id,
                "awesome": True,
                "text": "helloworld",
                "user": {"id": response["message"]["user"]["id"]},
            }
        )

    def test_delete_message(self, client, channel, random_user):
        msg_id = str(uuid.uuid4())
        channel.send_message({"id": msg_id, "text": "helloworld"}, random_user["id"])
        client.delete_message(msg_id)

    def test_query_users_young_hobbits(self, client, fellowship_of_the_ring):
        response = client.query_users({"race": {"$eq": "Hobbit"}}, {"age": -1})
        assert len(response["users"]) == 4
        assert [50, 38, 36, 28] == [u["age"] for u in response["users"]]

    def test_query_channels_members_in(self, client, fellowship_of_the_ring):
        response = client.query_channels({"members": {"$in": ["gimli"]}}, {"id": 1})
        assert len(response["channels"]) == 1
        assert response["channels"][0]["channel"]["id"] == "fellowship-of-the-ring"
        assert len(response["channels"][0]["members"]) == 9

    def test_devices(self, client, random_user):
        response = client.get_devices(random_user["id"])
        assert "devices" in response
        assert len(response["devices"]) == 0

        client.add_device(str(uuid.uuid4()), "apn", random_user["id"])
        response = client.get_devices(random_user["id"])
        assert len(response["devices"]) == 1

        client.delete_device(response["devices"][0]["id"], random_user["id"])
        client.add_device(str(uuid.uuid4()), "apn", random_user["id"])
        response = client.get_devices(random_user["id"])
        assert len(response["devices"]) == 1
