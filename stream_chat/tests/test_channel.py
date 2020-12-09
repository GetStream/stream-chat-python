import uuid

import pytest

from stream_chat.base.exceptions import StreamAPIException


@pytest.mark.incremental
class TestChannel(object):
    def test_ban_user(self, channel, random_user, server_user):
        channel.ban_user(random_user["id"], user_id=server_user["id"])
        channel.ban_user(
            random_user["id"],
            timeout=3600,
            reason="offensive language is not allowed here",
            user_id=server_user["id"],
        )
        channel.unban_user(random_user["id"])

    def test_create_without_id(self, client, random_users):
        channel = client.channel(
            "messaging", data={"members": [u["id"] for u in random_users]}
        )
        assert channel.id is None

        channel.create(random_users[0]["id"])
        assert channel.id is not None

    def test_send_event(self, channel, random_user):
        response = channel.send_event({"type": "typing.start"}, random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "typing.start"

    def test_send_reaction(self, channel, random_user):
        msg = channel.send_message({"text": "hi"}, random_user["id"])
        response = channel.send_reaction(
            msg["message"]["id"], {"type": "love"}, random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 1
        assert response["message"]["latest_reactions"][0]["type"] == "love"

    def test_delete_reaction(self, channel, random_user):
        msg = channel.send_message({"text": "hi"}, random_user["id"])
        channel.send_reaction(msg["message"]["id"], {"type": "love"}, random_user["id"])
        response = channel.delete_reaction(
            msg["message"]["id"], "love", random_user["id"]
        )
        assert "message" in response
        assert len(response["message"]["latest_reactions"]) == 0

    def test_update(self, channel):
        response = channel.update({"motd": "one apple a day..."})
        assert "channel" in response
        assert response["channel"]["motd"] == "one apple a day..."

    def test_delete(self, channel):
        response = channel.delete()
        assert "channel" in response
        assert response["channel"].get("deleted_at") is not None

    def test_truncate(self, channel):
        response = channel.truncate()
        assert "channel" in response

    def test_add_members(self, channel, random_user):
        response = channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = channel.add_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert not response["members"][0].get("is_moderator", False)

    def test_invite_members(self, channel, random_user):
        response = channel.remove_members([random_user["id"]])
        assert len(response["members"]) == 0

        response = channel.invite_members([random_user["id"]])
        assert len(response["members"]) == 1
        assert response["members"][0].get("invited", True)

    def test_add_moderators(self, channel, random_user):
        response = channel.add_moderators([random_user["id"]])
        assert response["members"][0]["is_moderator"]

        response = channel.demote_moderators([random_user["id"]])
        assert not response["members"][0].get("is_moderator", False)

    def test_mark_read(self, channel, random_user):
        response = channel.mark_read(random_user["id"])
        assert "event" in response
        assert response["event"]["type"] == "message.read"

    def test_get_replies(self, channel, random_user):
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

    def test_get_reactions(self, channel, random_user):
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

    def test_send_and_delete_file(self, channel, random_user):
        url = "https://homepages.cae.wisc.edu/~ece533/images/lena.png"
        resp = channel.send_file(url, "lena.png", random_user)
        assert "lena.png" in resp["file"]
        resp = channel.delete_file(resp["file"])

    def test_send_and_delete_image(self, channel, random_user):
        url = "https://homepages.cae.wisc.edu/~ece533/images/lena.png"
        resp = channel.send_image(
            url, "lena.png", random_user, content_type="image/png"
        )
        assert "lena.png" in resp["file"]
        # resp = channel.delete_image(resp['file'])

    def test_send_image_with_bot_blocked(self, channel, random_user):
        # following url blocks bots and we set a generic header to skip it
        # but it can start failing again, see initial discussion here: https://github.com/GetStream/stream-chat-python/pull/30#discussion_r444209891
        url = "https://api.twilio.com/2010-04-01/Accounts/AC3e136e1a00279f4dadcb10a9f1a1e8a3/Messages/MM547edf6f4846a30231c3033fa20f8419/Media/ME498020f8fe0b0ba2ff83ac99e4782e02"
        resp = channel.send_image(url, "js.png", random_user, content_type="image/png")
        assert "js.png" in resp["file"]

    def test_channel_hide_show(self, client, channel, random_users):
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

    def test_invites(self, client, channel):
        members = ["john", "paul", "george", "pete", "ringo", "eric"]
        client.update_users([{"id": m} for m in members])
        channel = client.channel(
            "team",
            "beatles-" + str(uuid.uuid4()),
            {"members": members, "invites": ["ringo", "eric"]},
        )
        channel.create("john")
        # accept the invite when not a member
        with pytest.raises(StreamAPIException):
            channel.accept_invite("brian")
        # accept the invite when a member
        accept = channel.accept_invite("ringo")
        for m in accept["members"]:
            if m["user_id"] == "ringo":
                assert m["invited"] is True
                assert "invite_accepted_at" in m
        # can accept again, noop
        channel.accept_invite("ringo")

        reject = channel.reject_invite("eric")
        for m in reject["members"]:
            if m["user_id"] == "eric":
                assert m["invited"] is True
                assert "invite_rejected_at" in m
        # cannot reject again, noop
        channel.reject_invite("eric")

    def test_query_members(self, client, channel):
        members = ["paul", "george", "john", "jessica", "john2"]
        client.update_users([{"id": m, "name": m} for m in members])
        for member in members:
            channel.add_members([member])

        response = channel.query_members(
            filter_conditions={"name": {"$autocomplete": "j"}},
            sort=[{"field": "created_at", "direction": 1}],
            offset=1,
            limit=10,
        )

        assert len(response) == 2
        assert response[0]["user"]["id"] == "jessica"
        assert response[1]["user"]["id"] == "john2"
