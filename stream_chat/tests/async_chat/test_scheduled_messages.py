from datetime import datetime, timedelta, timezone
from typing import Dict

import pytest

from stream_chat.async_chat import StreamChatAsync


async def schedule_message(channel, user_id: str) -> Dict:
    """Schedules a message an hour ahead.

    The CI app has scheduled messages enabled, so a disabled feature or a
    response without ``scheduled_message`` is a failure, not a skip.
    """
    response = await channel.send_message(
        {"text": "scheduled hello"},
        user_id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    assert "scheduled_message" in response, response
    return response["scheduled_message"]


class TestScheduledMessages:
    @pytest.mark.asyncio
    async def test_scheduled_message_lifecycle(
        self, client: StreamChatAsync, channel, random_user
    ):
        scheduled = await schedule_message(channel, random_user["id"])
        assert scheduled["cid"] == channel.cid
        assert scheduled["status"] == "scheduled"

        response = await client.query_scheduled_messages(
            random_user["id"], filter={"cid": channel.cid}
        )
        assert [m["id"] for m in response["scheduled_messages"]] == [scheduled["id"]]

        response = await client.update_scheduled_message(
            scheduled["id"], message={"text": "edited"}
        )
        assert response["scheduled_message"]["message"]["text"] == "edited"

        response = await client.delete_scheduled_message(scheduled["id"])
        assert response["scheduled_message"]["id"] == scheduled["id"]

    @pytest.mark.asyncio
    async def test_send_scheduled_message_now(
        self, client: StreamChatAsync, channel, random_user
    ):
        scheduled = await schedule_message(channel, random_user["id"])

        response = await client.send_scheduled_message_now(scheduled["id"])
        assert response["scheduled_message"]["id"] == scheduled["id"]
