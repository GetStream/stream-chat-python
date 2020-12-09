import uuid

import pytest

from stream_chat.base.exceptions import StreamAPIException


@pytest.mark.incremental
class TestChannel(object):
    @pytest.mark.asyncio
    async def test_ban_user(self, event_loop, channel, random_user, server_user):
        await channel.ban_user(random_user["id"], user_id=server_user["id"])
        await channel.ban_user(
            random_user["id"],
            timeout=3600,
            reason="offensive language is not allowed here",
            user_id=server_user["id"],
        )
        await channel.unban_user(random_user["id"])

    @pytest.mark.asyncio
    async def test_create_without_id(self, event_loop, client, random_users):
        channel = client.channel(
            "messaging", data={"members": [u["id"] for u in random_users]}
        )
        assert channel.id is None

        await channel.create(random_users[0]["id"])
        assert channel.id is not None

    @pytest.mark.asyncio
    async def test_send_event(self, event_loop, channel, random_user):
        response = await channel.send_event({"type": "typing.start"}, random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "typing.start"

    @pytest.mark.asyncio
    async def test_send_reaction(self, event_loop, channel, random_user):
        msg = await channel.send_message({"text": "hi"}, random_user["id"])
        response = await channel.send_reaction(
            msg["message"]["id"], {"type": "love"}, random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 1
        assert response["message"]["latest_reactions"][0]["type"] == "love"

    @pytest.mark.asyncio
    async def test_delete_reaction(self, event_loop, channel, random_user):
        msg = await channel.send_message({"text": "hi"}, random_user["id"])
        await channel.send_reaction(
            msg["message"]["id"], {"type": "love"}, random_user["id"]
        )
        response = await channel.delete_reaction(
            msg["message"]["id"], "love", random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 0

    @pytest.mark.asyncio
    async def test_update(self, event_loop, channel):
        response = await channel.update({"motd": "one apple a day..."})
        assert "channel" in response
        assert response["channel"]["motd"] == "one apple a day..."

    @pytest.mark.asyncio
    async def test_delete(self, event_loop, channel):
        response = await channel.delete()
        assert "channel" in response
        assert response["channel"].get("deleted_at") is not None

    @pytest.mark.asyncio
    async def test_truncate(self, event_loop, channel):
        response = await channel.truncate()
        assert "channel" in response

    @pytest.mark.asyncio
    async def test_add_members(self, event_loop, channel, random_user):
        response = await channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = await channel.add_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert not response["members"][0].get("is_moderator", False)

    @pytest.mark.asyncio
    async def test_invite_members(self, event_loop, channel, random_user):
        response = await channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = await channel.invite_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert response["members"][0].get("invited", True)

    @pytest.mark.asyncio
    async def test_add_moderators(self, event_loop, channel, random_user):
        response = await channel.add_moderators([random_user["id"]])
        assert response["members"][0]["is_moderator"]

        response = await channel.demote_moderators([random_user["id"]])
        assert not response["members"][0].get("is_moderator", False)

    @pytest.mark.asyncio
    async def test_mark_read(self, event_loop, channel, random_user):
        response = await channel.mark_read(random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "message.read"

    @pytest.mark.asyncio
    async def test_get_replies(self, event_loop, channel, random_user):
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

    @pytest.mark.asyncio
    async def test_get_reactions(self, event_loop, channel, random_user):
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

    @pytest.mark.asyncio
    async def test_send_and_delete_file(self, event_loop, channel, random_user):
        url = "https://homepages.cae.wisc.edu/~ece533/images/lena.png"
        resp = await channel.send_file(url, "lena.png", random_user)
        assert "lena.png" in resp["file"]
        resp = await channel.delete_file(resp["file"])

    @pytest.mark.asyncio
    async def test_send_and_delete_image(self, event_loop, channel, random_user):
        url = "https://homepages.cae.wisc.edu/~ece533/images/lena.png"
        resp = await channel.send_image(
            url, "lena.png", random_user, content_type="image/png"
        )
        assert "lena.png" in resp["file"]
        # resp = channel.delete_image(resp['file'])

    @pytest.mark.asyncio
    async def test_send_image_with_bot_blocked(self, event_loop, channel, random_user):
        # following url blocks bots and we set a generic header to skip it
        # but it can start failing again, see initial discussion here: https://github.com/GetStream/stream-chat-python/pull/30#discussion_r444209891
        url = "https://api.twilio.com/2010-04-01/Accounts/AC3e136e1a00279f4dadcb10a9f1a1e8a3/Messages/MM547edf6f4846a30231c3033fa20f8419/Media/ME498020f8fe0b0ba2ff83ac99e4782e02"
        resp = await channel.send_image(
            url, "js.png", random_user, content_type="image/png"
        )
        assert "js.png" in resp["file"]

    @pytest.mark.asyncio
    async def test_channel_hide_show(self, event_loop, client, channel, random_users):
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

    @pytest.mark.asyncio
    async def test_invites(self, event_loop, client, channel):
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

    @pytest.mark.asyncio
    async def test_query_members(self, event_loop, client, channel):
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
