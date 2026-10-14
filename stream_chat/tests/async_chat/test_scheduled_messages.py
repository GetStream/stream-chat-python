from datetime import datetime, timedelta, timezone
from typing import Dict

import pytest

from stream_chat.async_chat import StreamChatAsync
from stream_chat.base.exceptions import StreamAPIException


async def schedule_message(channel, user_id: str) -> Dict:
    """Schedules a message, skipping the test when the app cannot schedule.

    Scheduled messages are enabled per app by Stream, not through the app
    settings API, so the CI app cannot be baselined into having them.
    """
    try:
        response = await channel.send_message(
            {"text": "scheduled hello"},
            user_id,
            scheduled_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    except StreamAPIException as e:
        if "scheduled_messages_disabled" in e.response_text:
            pytest.skip("scheduled messages are not enabled for this app")
        raise
    if "scheduled_message" not in response:
        pytest.skip("the API does not support scheduled messages yet")
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
