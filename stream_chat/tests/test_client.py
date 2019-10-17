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

    def test_update_channel_type(self, client):
        response = client.update_channel_type("team", commands=["ban", "unban"])
        assert "commands" in response
        assert response["commands"] == ["ban", "unban"]

    def test_create_token(self, client):
        token = client.create_token("tommaso")
        payload = jwt.decode(token, client.api_secret, algorithms=["HS256"])
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

    def test_update_user_partial(self, client):
        user_id = str(uuid.uuid4())
        client.update_user({"id": user_id, "field": "value"})
        
        response = client.update_user_partial({
            "id": user_id,
            "set": {
                "field": "updated"
            }
        })

        assert "users" in response
        assert user_id in response["users"]
        assert response["users"][user_id]["field"] == "updated"

    def test_delete_user(self, client, random_user):
        response = client.delete_user(random_user["id"])
        assert "user" in response
        assert random_user["id"] == response["user"]["id"]

    def test_deactivate_user(self, client, random_user):
        response = client.deactivate_user(random_user["id"])
        assert "user" in response
        assert random_user["id"] == response["user"]["id"]

    def test_reactivate_user(self, client, random_user):
        response = client.deactivate_user(random_user["id"])
        assert "user" in response
        assert random_user["id"] == response["user"]["id"]
        response = client.reactivate_user(random_user["id"])
        assert "user" in response
        assert random_user["id"] == response["user"]["id"]

    def test_export_user(self, client, fellowship_of_the_ring):
        response = client.export_user("gandalf")
        assert "user" in response
        assert response["user"]["name"] == "Gandalf the Grey"

    def test_ban_user(self, client, random_user, server_user):
        client.ban_user(random_user["id"], user_id=server_user["id"])

    def test_unban_user(self, client, random_user, server_user):
        client.ban_user(random_user["id"], user_id=server_user["id"])
        client.unban_user(random_user["id"], user_id=server_user["id"])

    def test_flag_user(self, client, random_user, server_user):
        client.flag_user(random_user["id"], user_id=server_user["id"])

    def test_unflag_user(self, client, random_user, server_user):
        client.flag_user(random_user["id"], user_id=server_user["id"])
        client.unflag_user(random_user["id"], user_id=server_user["id"])

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
        msg_id = str(uuid.uuid4())
        channel.send_message({"id": msg_id, "text": "helloworld"}, random_user["id"])
        resp = client.delete_message(msg_id, hard=True)

    def test_flag_message(self, client, channel, random_user, server_user):
        msg_id = str(uuid.uuid4())
        channel.send_message({"id": msg_id, "text": "helloworld"}, random_user["id"])
        client.flag_message(msg_id, user_id=server_user["id"])

    def test_unflag_message(self, client, channel, random_user, server_user):
        msg_id = str(uuid.uuid4())
        channel.send_message({"id": msg_id, "text": "helloworld"}, random_user["id"])
        client.flag_message(msg_id, user_id=server_user["id"])
        client.unflag_message(msg_id, user_id=server_user["id"])

    def test_query_users_young_hobbits(self, client, fellowship_of_the_ring):
        response = client.query_users({"race": {"$eq": "Hobbit"}}, {"age": -1})
        assert len(response["users"]) == 4
        assert [50, 38, 36, 28] == [u["age"] for u in response["users"]]

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

    def test_search(self, client, channel, random_user):
        query = "supercalifragilisticexpialidocious"
        channel.send_message({"text": "How many syllables are there in {}?".format(query)}, random_user['id'])
        channel.send_message({"text": "Does 'cious' count as one or two?"}, random_user['id'])
        response = client.search(
            {"type": "messaging"},
            query,
            **{"limit": 2, "offset": 0}
        )
        # searches all channels so make sure at least one is found
        assert len(response['results']) >= 1
        assert query in response['results'][0]['message']['text']
        response = client.search(
            {"type": "messaging"},
            "cious",
            **{"limit": 12, "offset": 0})
        for message in response['results']:
            assert query not in message['message']['text']

    def test_query_channels_members_in(self, client, fellowship_of_the_ring):
        response = client.query_channels({"members": {"$in": ["gimli"]}}, {"id": 1})
        assert len(response["channels"]) == 1
        assert response["channels"][0]["channel"]["id"] == "fellowship-of-the-ring"
        assert len(response["channels"][0]["members"]) == 9

