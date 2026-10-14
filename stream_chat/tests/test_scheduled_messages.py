from datetime import datetime, timedelta, timezone
from typing import Dict

import pytest

from stream_chat import StreamChat
from stream_chat.base.exceptions import StreamAPIException


def schedule_message(channel, user_id: str) -> Dict:
    """Schedules a message, skipping the test when the app cannot schedule.

    Scheduled messages are enabled per app by Stream, not through the app
    settings API, so the CI app cannot be baselined into having them.
    """
    try:
        response = channel.send_message(
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
    def test_scheduled_message_lifecycle(
        self, client: StreamChat, channel, random_user
    ):
        scheduled = schedule_message(channel, random_user["id"])
        assert scheduled["cid"] == channel.cid
        assert scheduled["user"]["id"] == random_user["id"]
        assert scheduled["status"] == "scheduled"
        assert scheduled["message"]["text"] == "scheduled hello"

        response = client.query_scheduled_messages(
            random_user["id"], filter={"cid": channel.cid}
        )
        assert [m["id"] for m in response["scheduled_messages"]] == [scheduled["id"]]
        assert response["scheduled_messages"][0]["channel"]["cid"] == channel.cid

        response = client.update_scheduled_message(
            scheduled["id"],
            message={"text": "edited"},
            scheduled_at=datetime.now(timezone.utc) + timedelta(hours=2),
        )
        assert response["scheduled_message"]["message"]["text"] == "edited"

        response = client.delete_scheduled_message(scheduled["id"])
        assert response["scheduled_message"]["id"] == scheduled["id"]

        response = client.query_scheduled_messages(
            random_user["id"], filter={"cid": channel.cid}
        )
        assert response["scheduled_messages"] == []

    def test_send_scheduled_message_now(self, client: StreamChat, channel, random_user):
        scheduled = schedule_message(channel, random_user["id"])

        response = client.send_scheduled_message_now(scheduled["id"])
        assert response["scheduled_message"]["id"] == scheduled["id"]
