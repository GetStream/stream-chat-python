import uuid
from typing import Dict

import pytest

from stream_chat.async_chat.channel import Channel
from stream_chat.async_chat.client import StreamChatAsync
from stream_chat.types.base import SortOrder


@pytest.mark.incremental
class TestDraft:
    async def test_create_draft(self, channel: Channel, random_user: Dict):
        draft_message = {"text": "This is a draft message"}
        response = await channel.create_draft(draft_message, random_user["id"])

        assert "draft" in response
        assert response["draft"]["message"]["text"] == "This is a draft message"
        assert response["draft"]["channel_cid"] == channel.cid

    async def test_get_draft(self, channel: Channel, random_user: Dict):
        # First create a draft
        draft_message = {"text": "This is a draft to retrieve"}
        await channel.create_draft(draft_message, random_user["id"])

        # Then get the draft
        response = await channel.get_draft(random_user["id"])

        assert "draft" in response
        assert response["draft"]["message"]["text"] == "This is a draft to retrieve"
        assert response["draft"]["channel_cid"] == channel.cid

    async def test_delete_draft(self, channel: Channel, random_user: Dict):
        # First create a draft
        draft_message = {"text": "This is a draft to delete"}
        await channel.create_draft(draft_message, random_user["id"])

        # Then delete the draft
        await channel.delete_draft(random_user["id"])

        # Verify it's deleted by trying to get it
        try:
            await channel.get_draft(random_user["id"])
            raise AssertionError("Draft should be deleted")
        except Exception:
            # Expected behavior, draft should not be found
            pass

    async def test_thread_draft(self, channel: Channel, random_user: Dict):
        # First create a parent message
        msg = await channel.send_message({"text": "Parent message"}, random_user["id"])
        parent_id = msg["message"]["id"]

        # Create a draft reply
        draft_reply = {"text": "This is a draft reply", "parent_id": parent_id}
        response = await channel.create_draft(draft_reply, random_user["id"])

        assert "draft" in response
        assert response["draft"]["message"]["text"] == "This is a draft reply"
        assert response["draft"]["parent_id"] == parent_id

        # Get the draft reply
        response = await channel.get_draft(random_user["id"], parent_id=parent_id)

        assert "draft" in response
        assert response["draft"]["message"]["text"] == "This is a draft reply"
        assert response["draft"]["parent_id"] == parent_id

        # Delete the draft reply
        await channel.delete_draft(random_user["id"], parent_id=parent_id)

        # Verify it's deleted
        try:
            await channel.get_draft(random_user["id"], parent_id=parent_id)
            raise AssertionError("Thread draft should be deleted")
        except Exception:
            # Expected behavior
            pass

    async def test_query_drafts(
        self, client: StreamChatAsync, channel: Channel, random_user: Dict
    ):
        # Create multiple drafts in different channels
        draft1 = {"text": "Draft in channel 1"}
        await channel.create_draft(draft1, random_user["id"])

        # Create another channel with a draft
        channel2 = client.channel("messaging", str(uuid.uuid4()))
        await channel2.create(random_user["id"])

        draft2 = {"text": "Draft in channel 2"}
        await channel2.create_draft(draft2, random_user["id"])

        # Query all drafts for the user
        response = await client.query_drafts(random_user["id"])

        assert "drafts" in response
        assert len(response["drafts"]) == 2

        # Query drafts for a specific channel
        response = await client.query_drafts(
            random_user["id"], filter={"channel_cid": channel2.cid}
        )

        assert "drafts" in response
        assert len(response["drafts"]) == 1
        draft = response["drafts"][0]
        assert draft["channel_cid"] == channel2.cid
        assert draft["message"]["text"] == "Draft in channel 2"

        # Query drafts with sort
        response = await client.query_drafts(
            random_user["id"],
            sort=[{"field": "created_at", "direction": SortOrder.ASC}],
        )

        assert "drafts" in response
        assert len(response["drafts"]) == 2
        assert response["drafts"][0]["channel_cid"] == channel.cid
        assert response["drafts"][1]["channel_cid"] == channel2.cid

        # Query drafts with pagination
        response = await client.query_drafts(
            random_user["id"],
            options={"limit": 1},
        )

        assert "drafts" in response
        assert len(response["drafts"]) == 1
        assert response["drafts"][0]["channel_cid"] == channel2.cid

        assert response["next"] is not None

        # Query drafts with pagination
        response = await client.query_drafts(
            random_user["id"],
            options={"limit": 1, "next": response["next"]},
        )

        assert "drafts" in response
        assert len(response["drafts"]) == 1
        assert response["drafts"][0]["channel_cid"] == channel.cid

        # Cleanup
        try:
            await channel2.delete()
        except Exception:
            pass
