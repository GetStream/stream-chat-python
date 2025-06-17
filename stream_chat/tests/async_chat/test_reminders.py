from datetime import datetime, timedelta, timezone

import pytest

from stream_chat.async_chat import StreamChatAsync
from stream_chat.base.exceptions import StreamAPIException


class TestReminders:
    @pytest.fixture(autouse=True)
    @pytest.mark.asyncio
    async def setup_channel_for_reminders(self, channel: "Channel"):
        await channel.update_partial(
            {"config_overrides": {"user_message_reminders": True}},
        )
        yield
        await channel.update_partial(
            {"config_overrides": {"user_message_reminders": False}},
        )

    @pytest.mark.asyncio
    async def test_create_reminder(self, client: StreamChatAsync, channel, random_user):
        # First, send a message to create a reminder for
        message_data = {
            "text": "This is a test message for reminder",
        }
        response = await channel.send_message(message_data, random_user["id"])
        message_id = response["message"]["id"]

        # Create a reminder without remind_at
        response = await client.create_reminder(message_id, random_user["id"])
        # Verify the response contains the expected data
        assert response is not None
        assert "reminder" in response
        assert response["reminder"]["message_id"] == message_id
        assert "user_id" in response["reminder"]

        # Clean up - try to delete the reminder
        try:
            await client.delete_reminder(message_id, random_user["id"])
        except StreamAPIException:
            pass  # It's okay if deletion fails

    @pytest.mark.asyncio
    async def test_create_reminder_with_remind_at(
        self, client: StreamChatAsync, channel, random_user
    ):
        # First, send a message to create a reminder for
        message_data = {
            "text": "This is a test message for reminder with time",
        }
        response = await channel.send_message(message_data, random_user["id"])
        message_id = response["message"]["id"]

        # Create a reminder with remind_at
        remind_at = datetime.now(timezone.utc) + timedelta(days=1)
        response = await client.create_reminder(
            message_id, random_user["id"], remind_at
        )
        # Verify the response contains the expected data
        assert response is not None
        assert "reminder" in response
        assert response["reminder"]["message_id"] == message_id
        assert "user_id" in response["reminder"]
        assert "remind_at" in response["reminder"]

        # Clean up - try to delete the reminder
        try:
            await client.delete_reminder(message_id, random_user["id"])
        except StreamAPIException:
            pass  # It's okay if deletion fails

    @pytest.mark.asyncio
    async def test_update_reminder(self, client: StreamChatAsync, channel, random_user):
        # First, send a message to create a reminder for
        message_data = {
            "text": "This is a test message for updating reminder",
        }
        response = await channel.send_message(message_data, random_user["id"])
        message_id = response["message"]["id"]

        # Create a reminder
        await client.create_reminder(message_id, random_user["id"])

        # Update the reminder with a remind_at time
        remind_at = datetime.now(timezone.utc) + timedelta(days=2)
        response = await client.update_reminder(
            message_id, random_user["id"], remind_at
        )
        # Verify the response contains the expected data
        assert response is not None
        assert "reminder" in response
        assert response["reminder"]["message_id"] == message_id
        assert "user_id" in response["reminder"]
        assert "remind_at" in response["reminder"]

        # Clean up - try to delete the reminder
        try:
            await client.delete_reminder(message_id, random_user["id"])
        except StreamAPIException:
            pass  # It's okay if deletion fails

    @pytest.mark.asyncio
    async def test_delete_reminder(self, client: StreamChatAsync, channel, random_user):
        # First, send a message to create a reminder for
        message_data = {
            "text": "This is a test message for deleting reminder",
        }
        response = await channel.send_message(message_data, random_user["id"])
        message_id = response["message"]["id"]

        # Create a reminder
        await client.create_reminder(message_id, random_user["id"])

        # Delete the reminder
        response = await client.delete_reminder(message_id, random_user["id"])
        # Verify the response contains the expected data
        assert response is not None
        # The delete response may not include the reminder object

    @pytest.mark.asyncio
    async def test_query_reminders(self, client: StreamChatAsync, channel, random_user):
        # First, send messages to create reminders for
        message_ids = []
        channel_cid = channel.cid

        for i in range(3):
            message_data = {
                "text": f"This is test message {i} for querying reminders",
            }
            response = await channel.send_message(message_data, random_user["id"])
            message_id = response["message"]["id"]
            message_ids.append(message_id)

            # Create a reminder with different remind_at times
            remind_at = datetime.now(timezone.utc) + timedelta(hours=i + 1)
            await client.create_reminder(message_id, random_user["id"], remind_at)

        # Test case 1: Query reminders without filters
        response = await client.query_reminders(random_user["id"])
        assert response is not None
        assert "reminders" in response
        # Check that we have at least our 3 reminders
        assert len(response["reminders"]) >= 3

        # Check that at least some of our message IDs are in the results
        found_ids = [
            r["message_id"]
            for r in response["reminders"]
            if r["message_id"] in message_ids
        ]
        assert len(found_ids) > 0

        # Test case 2: Query reminders by message ID
        if len(message_ids) > 0:
            filter_conditions = {"message_id": {"$in": [message_ids[0]]}}
            response = await client.query_reminders(
                random_user["id"], filter_conditions
            )
            assert response is not None

        # Test case 3: Query reminders by channel CID
        filter_conditions = {"channel_cid": channel_cid}
        response = await client.query_reminders(random_user["id"], filter_conditions)
        assert response is not None

        # Clean up - try to delete the reminders
        for message_id in message_ids:
            try:
                await client.delete_reminder(message_id, random_user["id"])
            except StreamAPIException:
                pass  # It's okay if deletion fails
