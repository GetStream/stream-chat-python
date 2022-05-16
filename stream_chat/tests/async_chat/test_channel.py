import time
import uuid
from pathlib import Path
from typing import Dict, List

import pytest

from stream_chat.async_chat.channel import Channel
from stream_chat.async_chat.client import StreamChatAsync
from stream_chat.base.exceptions import StreamAPIException


@pytest.mark.incremental
class TestChannel:
    async def test_ban_user(
        self, channel: Channel, random_user: Dict, server_user: Dict
    ):
        await channel.ban_user(random_user["id"], user_id=server_user["id"])
        await channel.ban_user(
            random_user["id"],
            timeout=3600,
            reason="offensive language is not allowed here",
            user_id=server_user["id"],
        )
        await channel.unban_user(random_user["id"])

    async def test_create_without_id(
        self, client: StreamChatAsync, random_users: List[Dict]
    ):
        channel = client.channel(
            "messaging", data={"members": [u["id"] for u in random_users]}
        )
        assert channel.id is None

        await channel.create(random_users[0]["id"])
        assert channel.id is not None

    async def test_send_message_with_options(self, channel: Channel, random_user: Dict):
        response = await channel.send_message(
            {"text": "hi"}, random_user["id"], skip_push=True
        )
        assert "message" in response
        assert response["message"]["text"] == "hi"

    async def test_send_event(self, channel: Channel, random_user: Dict):
        response = await channel.send_event({"type": "typing.start"}, random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "typing.start"

    async def test_send_reaction(self, channel: Channel, random_user: Dict):
        msg = await channel.send_message({"text": "hi"}, random_user["id"])
        response = await channel.send_reaction(
            msg["message"]["id"], {"type": "love"}, random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 1
        assert response["message"]["latest_reactions"][0]["type"] == "love"

    async def test_delete_reaction(self, channel: Channel, random_user: Dict):
        msg = await channel.send_message({"text": "hi"}, random_user["id"])
        await channel.send_reaction(
            msg["message"]["id"], {"type": "love"}, random_user["id"]
        )
        response = await channel.delete_reaction(
            msg["message"]["id"], "love", random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 0

    async def test_update(self, channel: Channel):
        response = await channel.update({"motd": "one apple a day..."})
        assert "channel" in response
        assert response["channel"]["motd"] == "one apple a day..."

    async def test_update_partial(self, channel: Channel):
        response = await channel.update({"color": "blue", "age": 30})
        assert "channel" in response
        assert response["channel"]["color"] == "blue"
        assert response["channel"]["age"] == 30

        response = await channel.update_partial(
            to_set={"color": "red"}, to_unset=["age"]
        )
        assert "channel" in response
        assert response["channel"]["color"] == "red"
        assert "age" not in response["channel"]

    async def test_delete(self, channel: Channel):
        response = await channel.delete()
        assert "channel" in response
        assert response["channel"].get("deleted_at") is not None

    async def test_truncate(self, channel: Channel):
        response = await channel.truncate()
        assert "channel" in response

    async def test_truncate_with_options(self, channel: Channel, random_user: Dict):
        response = await channel.truncate(
            skip_push=True,
            message={
                "text": "Truncating channel.",
                "user_id": random_user["id"],
            },
        )
        assert "channel" in response

    async def test_add_members(self, channel: Channel, random_user: Dict):
        response = await channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = await channel.add_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert not response["members"][0].get("is_moderator", False)

    async def test_add_members_with_options(self, channel: Channel, random_user: Dict):
        response = await channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = await channel.add_members([random_user["id"]], hide_history=True)
        assert len(response["members"]) == 1

    async def test_invite_members(self, channel: Channel, random_user: Dict):
        response = await channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = await channel.invite_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert response["members"][0].get("invited", True)

    async def test_add_moderators(self, channel: Channel, random_user: Dict):
        response = await channel.add_moderators([random_user["id"]])
        assert response["members"][0]["is_moderator"]

        response = await channel.demote_moderators([random_user["id"]])
        assert not response["members"][0].get("is_moderator", False)

    async def test_assign_roles_moderators(self, channel: Channel, random_user: Dict):
        member = {"user_id": random_user["id"], "channel_role": "channel_moderator"}
        response = await channel.add_members([member])
        assert len(response["members"]) == 1
        assert response["members"][0]["channel_role"] == "channel_moderator"

        member["channel_role"] = "channel_member"
        response = await channel.assign_roles([member])
        assert len(response["members"]) == 1
        assert response["members"][0]["channel_role"] == "channel_member"

    async def test_get_messages(self, channel: Channel, random_user: Dict):
        msg_id = str(uuid.uuid4())
        await channel.send_message(
            {"id": msg_id, "text": "helloworld"}, random_user["id"]
        )
        resp = await channel.get_messages([msg_id])
        assert len(resp["messages"]) == 1

    async def test_mark_read(self, channel: Channel, random_user: Dict):
        response = await channel.mark_read(random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "message.read"

    async def test_get_replies(self, channel: Channel, random_user: Dict):
        msg = await channel.send_message({"text": "hi"}, random_user["id"])
        response = await channel.get_replies(msg["message"]["id"])
        assert "messages" in response
        assert len(response["messages"]) == 0

        for i in range(10):
            await channel.send_message(
                {"text": "hi", "index": i, "parent_id": msg["message"]["id"]},
                random_user["id"],
            )

        response = await channel.get_replies(msg["message"]["id"])
        assert "messages" in response
        assert len(response["messages"]) == 10

        response = await channel.get_replies(msg["message"]["id"], limit=3, offset=3)
        assert "messages" in response
        assert len(response["messages"]) == 3
        assert response["messages"][0]["index"] == 7

    async def test_get_reactions(self, channel: Channel, random_user: Dict):
        msg = await channel.send_message({"text": "hi"}, random_user["id"])
        response = await channel.get_reactions(msg["message"]["id"])

        assert "reactions" in response
        assert len(response["reactions"]) == 0

        await channel.send_reaction(
            msg["message"]["id"], {"type": "love", "count": 42}, random_user["id"]
        )

        await channel.send_reaction(
            msg["message"]["id"], {"type": "clap"}, random_user["id"]
        )

        response = await channel.get_reactions(msg["message"]["id"])
        assert len(response["reactions"]) == 2

        response = await channel.get_reactions(msg["message"]["id"], offset=1)
        assert len(response["reactions"]) == 1

        assert response["reactions"][0]["count"] == 42

    async def test_send_and_delete_file(self, channel: Channel, random_user: Dict):
        url = str(
            Path.joinpath(Path(__file__).parent.parent, "assets", "helloworld.jpg")
        )
        resp = await channel.send_file(url, "helloworld.jpg", random_user)
        assert "helloworld.jpg" in resp["file"]
        await channel.delete_file(resp["file"])

    async def test_send_and_delete_image(self, channel: Channel, random_user: Dict):
        url = str(
            Path.joinpath(Path(__file__).parent.parent, "assets", "helloworld.jpg")
        )
        resp = await channel.send_image(
            url, "helloworld.jpg", random_user, content_type="image/jpeg"
        )
        assert "helloworld.jpg" in resp["file"]
        await channel.delete_image(resp["file"])

    async def test_channel_hide_show(
        self, client: StreamChatAsync, channel: Channel, random_users: List[Dict]
    ):
        # setup
        await channel.add_members([u["id"] for u in random_users])
        # verify
        response = await client.query_channels({"id": channel.id})
        assert len(response["channels"]) == 1
        response = await client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1
        # hide
        await channel.hide(random_users[0]["id"])
        response = await client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 0
        # search hidden channels
        response = await client.query_channels(
            {"id": channel.id, "hidden": True}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1
        # unhide
        await channel.show(random_users[0]["id"])
        response = await client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1
        # hide again
        await channel.hide(random_users[0]["id"])
        response = await client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 0
        # send message
        await channel.send_message({"text": "hi"}, random_users[1]["id"])
        # channel should be listed now
        response = await client.query_channels(
            {"id": channel.id}, user_id=random_users[0]["id"]
        )
        assert len(response["channels"]) == 1

    async def test_invites(self, client: StreamChatAsync, channel: Channel):
        members = ["john", "paul", "george", "pete", "ringo", "eric"]
        await client.update_users([{"id": m} for m in members])
        channel = client.channel(
            "team",
            "beatles-" + str(uuid.uuid4()),
            {"members": members, "invites": ["ringo", "eric"]},
        )
        await channel.create("john")
        # accept the invite when not a member
        with pytest.raises(StreamAPIException):
            await channel.accept_invite("brian")
        # accept the invite when a member
        accept = await channel.accept_invite("ringo")
        for m in accept["members"]:
            if m["user_id"] == "ringo":
                assert m["invited"] is True
                assert "invite_accepted_at" in m
        # can accept again, noop
        await channel.accept_invite("ringo")

        reject = await channel.reject_invite("eric")
        for m in reject["members"]:
            if m["user_id"] == "eric":
                assert m["invited"] is True
                assert "invite_rejected_at" in m
        # can reject again, noop
        await channel.reject_invite("eric")

    async def test_query_members(self, client: StreamChatAsync, channel: Channel):
        members = ["paul", "george", "john", "jessica", "john2"]
        await client.update_users([{"id": m, "name": m} for m in members])
        for member in members:
            await channel.add_members([member])

        response = await channel.query_members(
            filter_conditions={"name": {"$autocomplete": "j"}},
            sort=[{"field": "created_at", "direction": 1}],
            offset=1,
            limit=10,
        )

        assert len(response) == 2
        assert response[0]["user"]["id"] == "jessica"
        assert response[1]["user"]["id"] == "john2"

    async def test_mute_unmute(
        self, client: StreamChatAsync, channel: Channel, random_users: List[Dict]
    ):
        user_id = random_users[0]["id"]
        response = await channel.mute(user_id, expiration=30000)
        assert "channel_mute" in response
        assert response["channel_mute"]["channel"]["cid"] == channel.cid
        assert response["channel_mute"]["user"]["id"] == user_id

        response = await client.query_channels(
            {"muted": True, "cid": channel.cid},
            user_id=user_id,
        )
        assert len(response["channels"]) == 1

        await channel.unmute(user_id)
        response = await client.query_channels(
            {"muted": True, "cid": channel.cid},
            user_id=user_id,
        )
        assert len(response["channels"]) == 0

    async def test_export_channel_status(
        self, client: StreamChatAsync, channel: Channel
    ):
        with pytest.raises(StreamAPIException, match=r".*Can't find task.*"):
            await client.get_export_channel_status(str(uuid.uuid4()))

        with pytest.raises(StreamAPIException, match=r".*Can't find channel.*"):
            await client.export_channel("messaging", str(uuid.uuid4()))

    async def test_export_channel(
        self, client: StreamChatAsync, channel: Channel, random_users: List[Dict]
    ):
        await channel.send_message({"text": "Hey Joni"}, random_users[0]["id"])

        resp = await client.export_channel(
            channel.channel_type, channel.id, include_truncated_messages=False
        )
        task_id = resp["task_id"]
        assert task_id != ""

        while True:
            resp = await client.get_export_channel_status(task_id)
            assert resp["status"] != ""
            assert resp["created_at"] != ""
            assert resp["updated_at"] != ""
            if resp["status"] == "completed":
                assert len(resp["result"]) != 0
                assert resp["result"]["url"] != ""
                assert "error" not in resp
                break
            time.sleep(0.5)
