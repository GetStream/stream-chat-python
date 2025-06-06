import time
import uuid
from pathlib import Path
from typing import Dict, List

import pytest

from stream_chat import StreamChat
from stream_chat.base.exceptions import StreamAPIException
from stream_chat.channel import Channel
from stream_chat.tests.conftest import hard_delete_users


@pytest.mark.incremental
class TestChannel:
    def test_ban_user(self, channel: Channel, random_user, server_user: Dict):
        channel.ban_user(random_user["id"], user_id=server_user["id"])
        channel.ban_user(
            random_user["id"],
            timeout=3600,
            reason="offensive language is not allowed here",
            user_id=server_user["id"],
        )
        channel.unban_user(random_user["id"])

    def test_create_without_id(self, client: StreamChat, random_users: List[Dict]):
        channel = client.channel(
            "messaging", data={"members": [u["id"] for u in random_users]}
        )
        assert channel.id is None

        channel.create(random_users[0]["id"])
        assert channel.id is not None

        client.delete_channels([channel.cid], hard_delete=True)

    def test_create_with_options(self, client: StreamChat, random_users: List[Dict]):
        channel = client.channel(
            "messaging", data={"members": [u["id"] for u in random_users]}
        )
        assert channel.id is None

        channel.create(random_users[0]["id"], hide_for_creator=True)
        assert channel.id is not None

        client.delete_channels([channel.cid], hard_delete=True)

    def test_send_message_with_options(self, channel: Channel, random_user: Dict):
        response = channel.send_message(
            {"text": "hi"}, random_user["id"], skip_push=True
        )
        assert "message" in response
        assert response["message"]["text"] == "hi"

    def test_send_pending_message(
        self, client: StreamChat, channel: Channel, random_user: Dict
    ):
        response = channel.send_message(
            {"text": "hi"},
            random_user["id"],
            pending=True,
            pending_message_metadata={"extra_data": "test"},
        )
        assert "message" in response
        assert response["message"]["text"] == "hi"

        response = client.commit_message(response["message"]["id"])
        assert "message" in response
        assert response["message"]["text"] == "hi"

    def test_send_message_with_restricted_visibility(
        self,
        channel: Channel,
        random_users: List[Dict],
    ):
        amy = random_users[0]["id"]
        paul = random_users[1]["id"]
        user = random_users[2]["id"]

        # Add users to channel
        channel.add_members([amy, paul])

        # Send message with restricted visibility
        response = channel.send_message(
            {"text": "hi", "restricted_visibility": [amy, paul]}, user
        )
        assert "message" in response
        assert response["message"]["text"] == "hi"
        assert response["message"]["restricted_visibility"] == [amy, paul]

    def test_send_event(self, channel: Channel, random_user: Dict):
        response = channel.send_event({"type": "typing.start"}, random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "typing.start"

    def test_send_reaction(self, channel: Channel, random_user: Dict):
        msg = channel.send_message({"text": "hi"}, random_user["id"])
        response = channel.send_reaction(
            msg["message"]["id"], {"type": "love"}, random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 1
        assert response["message"]["latest_reactions"][0]["type"] == "love"

    def test_delete_reaction(self, channel: Channel, random_user: Dict):
        msg = channel.send_message({"text": "hi"}, random_user["id"])
        channel.send_reaction(msg["message"]["id"], {"type": "love"}, random_user["id"])
        response = channel.delete_reaction(
            msg["message"]["id"], "love", random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 0

    def test_update(self, channel: Channel):
        response = channel.update({"motd": "one apple a day..."})
        assert "channel" in response
        assert response["channel"]["motd"] == "one apple a day..."

    def test_update_partial(self, channel: Channel):
        response = channel.update({"color": "blue", "age": 30})
        assert "channel" in response
        assert response["channel"]["color"] == "blue"
        assert response["channel"]["age"] == 30

        response = channel.update_partial(to_set={"color": "red"}, to_unset=["age"])
        assert "channel" in response
        assert response["channel"]["color"] == "red"
        assert "age" not in response["channel"]

    def test_delete(self, channel: Channel):
        response = channel.delete()
        assert "channel" in response
        assert response["channel"].get("deleted_at") is not None

    def test_truncate(self, channel: Channel):
        response = channel.truncate()
        assert "channel" in response

    def test_truncate_with_options(self, channel: Channel, random_user: Dict):
        response = channel.truncate(
            skip_push=True,
            message={
                "text": "Truncating channel.",
                "user_id": random_user["id"],
            },
        )
        assert "channel" in response

    def test_add_members(self, channel: Channel, random_user: Dict):
        response = channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = channel.add_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert not response["members"][0].get("is_moderator", False)

    def test_add_members_with_additional_options(
        self, channel: Channel, random_user: Dict
    ):
        response = channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = channel.add_members([random_user["id"]], hide_history=True)
        assert len(response["members"]) == 1

    def test_invite_members(self, channel: Channel, random_user: Dict):
        response = channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = channel.invite_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert response["members"][0].get("invited", True)

    def test_add_moderators(self, channel: Channel, random_user: Dict):
        response = channel.add_moderators([random_user["id"]])
        assert response["members"][0]["is_moderator"]

        response = channel.demote_moderators([random_user["id"]])
        assert not response["members"][0].get("is_moderator", False)

    def test_assign_roles_moderators(self, channel: Channel, random_user: Dict):
        member = {"user_id": random_user["id"], "channel_role": "channel_moderator"}
        response = channel.add_members([member])
        assert len(response["members"]) == 1
        assert response["members"][0]["channel_role"] == "channel_moderator"

        member["channel_role"] = "channel_member"
        response = channel.assign_roles([member])
        assert len(response["members"]) == 1
        assert response["members"][0]["channel_role"] == "channel_member"

    def test_mark_read(self, channel: Channel, random_user: Dict):
        response = channel.mark_read(random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "message.read"

    def test_mark_unread(self, channel: Channel, random_user: Dict):
        msg_id = str(uuid.uuid4())
        channel.send_message({"id": msg_id, "text": "helloworld"}, random_user["id"])
        response = channel.mark_unread(random_user["id"], message_id=msg_id)
        assert "duration" in response

    def test_get_messages(self, channel: Channel, random_user: Dict):
        msg_id = str(uuid.uuid4())
        channel.send_message({"id": msg_id, "text": "helloworld"}, random_user["id"])
        resp = channel.get_messages([msg_id])
        assert len(resp["messages"]) == 1

    def test_get_replies(self, channel: Channel, random_user: Dict):
        msg = channel.send_message({"text": "hi"}, random_user["id"])
        response = channel.get_replies(msg["message"]["id"])
        assert "messages" in response
        assert len(response["messages"]) == 0

        for i in range(10):
            channel.send_message(
                {"text": "hi", "index": i, "parent_id": msg["message"]["id"]},
                random_user["id"],
            )

        response = channel.get_replies(msg["message"]["id"])
        assert "messages" in response
        assert len(response["messages"]) == 10

        response = channel.get_replies(msg["message"]["id"], limit=3, offset=3)
        assert "messages" in response
        assert len(response["messages"]) == 3
        assert response["messages"][0]["index"] == 7

    def test_get_reactions(self, channel: Channel, random_user: Dict):
        msg = channel.send_message({"text": "hi"}, random_user["id"])
        response = channel.get_reactions(msg["message"]["id"])

        assert "reactions" in response
        assert len(response["reactions"]) == 0

        channel.send_reaction(
            msg["message"]["id"], {"type": "love", "count": 42}, random_user["id"]
        )

        channel.send_reaction(msg["message"]["id"], {"type": "clap"}, random_user["id"])

        response = channel.get_reactions(msg["message"]["id"])
        assert len(response["reactions"]) == 2

        response = channel.get_reactions(msg["message"]["id"], offset=1)
        assert len(response["reactions"]) == 1

        assert response["reactions"][0]["count"] == 42

    def test_send_and_delete_file(self, channel: Channel, random_user: Dict):
        url = str(Path.joinpath(Path(__file__).parent, "assets", "helloworld.jpg"))
        resp = channel.send_file(url, "helloworld.jpg", random_user)
        assert "helloworld.jpg" in resp["file"]
        channel.delete_file(resp["file"])

    def test_send_and_delete_image(self, channel: Channel, random_user: Dict):
        url = str(Path.joinpath(Path(__file__).parent, "assets", "helloworld.jpg"))
        resp = channel.send_image(
            url, "helloworld.jpg", random_user, content_type="image/jpeg"
        )
        assert "helloworld.jpg" in resp["file"]
        channel.delete_image(resp["file"])

    def test_channel_hide_show(
        self, client: StreamChat, channel: Channel, random_users
    ):
        # setup
        channel.add_members([u["id"] for u in random_users])
        # verify
        response = client.query_channels({"id": channel.id})
        assert len(response["channels"]) == 1
        response = client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1
        # hide
        channel.hide(random_users[0]["id"])
        response = client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 0
        # search hidden channels
        response = client.query_channels(
            {"id": channel.id, "hidden": True}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1
        # unhide
        channel.show(random_users[0]["id"])
        response = client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1
        # hide again
        channel.hide(random_users[0]["id"])
        response = client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 0
        # send message
        channel.send_message({"text": "hi"}, random_users[1]["id"])
        # channel should be listed now
        response = client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1

    def test_invites(self, client: StreamChat, random_users: List[Dict]):
        john = random_users[0]["id"]
        ringo = random_users[1]["id"]
        eric = random_users[2]["id"]

        members = [u["id"] for u in random_users]
        channel = client.channel(
            "team",
            "beatles-" + str(uuid.uuid4()),
            {"members": members, "invites": [ringo, eric]},
        )
        channel.create(john)
        # accept the invite when not a member
        with pytest.raises(StreamAPIException):
            channel.accept_invite("brian-" + str(uuid.uuid4()))
        # accept the invite when a member
        accept = channel.accept_invite(ringo)
        for m in accept["members"]:
            if m["user_id"] == ringo:
                assert m["invited"] is True
                assert "invite_accepted_at" in m
        # can accept again, noop
        channel.accept_invite(ringo)

        reject = channel.reject_invite(eric)
        for m in reject["members"]:
            if m["user_id"] == eric:
                assert m["invited"] is True
                assert "invite_rejected_at" in m
        # cannot reject again, noop
        channel.reject_invite(eric)
        channel.delete(hard=True)

    def test_query_members(self, client: StreamChat, channel: Channel):
        rand = str(uuid.uuid4())
        user_ids = ["paul", "george", "john", "jessica", "john2"]
        user_ids = [f"{n}-{rand}" for n in user_ids]
        client.upsert_users([{"id": m, "name": m} for m in user_ids])
        for member in user_ids:
            channel.add_members([member])

        response = channel.query_members(
            filter_conditions={"name": {"$autocomplete": "j"}},
            sort=[{"field": "created_at", "direction": 1}],
            offset=1,
            limit=10,
        )

        assert len(response) == 2
        assert response[0]["user"]["id"] == f"jessica-{rand}"
        assert response[1]["user"]["id"] == f"john2-{rand}"

        hard_delete_users(client, user_ids)

    def test_mute_unmute(
        self, client: StreamChat, channel: Channel, random_users: List[Dict]
    ):
        user_id = random_users[0]["id"]
        response = channel.mute(user_id, expiration=30000)
        assert "channel_mute" in response
        assert "expires" in response["channel_mute"]
        assert response["channel_mute"]["channel"]["cid"] == channel.cid
        assert response["channel_mute"]["user"]["id"] == user_id

        response = client.query_channels(
            {"muted": True, "cid": channel.cid}, user_id=user_id
        )
        assert len(response["channels"]) == 1

        channel.unmute(user_id)
        response = client.query_channels(
            {"muted": True, "cid": channel.cid},
            user_id=user_id,
        )
        assert len(response["channels"]) == 0

    def test_export_channel_status(self, client: StreamChat, channel: Channel):
        with pytest.raises(StreamAPIException, match=r".*Can't find task.*"):
            client.get_export_channel_status(str(uuid.uuid4()))

        with pytest.raises(StreamAPIException, match=r".*Can't find channel.*"):
            client.export_channel("messaging", str(uuid.uuid4()))

    def test_export_channel(
        self, client: StreamChat, channel: Channel, random_users: List[Dict]
    ):
        channel.send_message({"text": "Hey Joni"}, random_users[0]["id"])

        resp = client.export_channel(
            channel.channel_type, channel.id, include_truncated_messages=False
        )
        task_id = resp["task_id"]
        assert task_id != ""

        while True:
            resp = client.get_export_channel_status(task_id)
            assert resp["status"] != ""
            assert resp["created_at"] != ""
            assert resp["updated_at"] != ""
            if resp["status"] == "completed":
                assert len(resp["result"]) != 0
                assert resp["result"]["url"] != ""
                assert "error" not in resp
                break
            time.sleep(0.5)

    def test_pin_channel(
        self, client: StreamChat, channel: Channel, random_users: List[Dict]
    ):
        user_id = random_users[0]["id"]
        channel.add_members([user_id])

        # Pin the channel
        response = channel.pin(user_id)
        assert response is not None

        # Query for pinned channels
        response = client.query_channels(
            {"pinned": True, "cid": channel.cid}, user_id=user_id
        )
        assert len(response["channels"]) == 1
        assert response["channels"][0]["channel"]["cid"] == channel.cid

        # Unpin the channel
        response = channel.unpin(user_id)
        assert response is not None

        # Query for pinned channels
        response = client.query_channels(
            {"pinned": False, "cid": channel.cid}, user_id=user_id
        )
        assert len(response["channels"]) == 1
        assert response["channels"][0]["channel"]["cid"] == channel.cid

    def test_archive_channel(
        self, client: StreamChat, channel: Channel, random_users: List[Dict]
    ):
        user_id = random_users[0]["id"]
        channel.add_members([user_id])

        # Archive the channel
        response = channel.archive(user_id)
        assert response is not None

        # Query for archived channels
        response = client.query_channels(
            {"archived": True, "cid": channel.cid}, user_id=user_id
        )
        assert len(response["channels"]) == 1
        assert response["channels"][0]["channel"]["cid"] == channel.cid

        # Unarchive the channel
        response = channel.unarchive(user_id)
        assert response is not None

        # Query for archhived channels
        response = client.query_channels(
            {"archived": False, "cid": channel.cid}, user_id=user_id
        )
        assert len(response["channels"]) == 1
        assert response["channels"][0]["channel"]["cid"] == channel.cid

    def test_update_member_partial(self, channel: Channel, random_users: List[Dict]):
        user_id = random_users[0]["id"]
        channel.add_members([user_id])

        # Test setting a custom field
        response = channel.update_member_partial(user_id, to_set={"hat": "blue"})
        assert response["channel_member"]["hat"] == "blue"

        # Test setting a new field while unsetting the previous one
        response = channel.update_member_partial(
            user_id, to_set={"color": "red"}, to_unset=["hat"]
        )
        assert response["channel_member"]["color"] == "red"
        assert "hat" not in response["channel_member"]
