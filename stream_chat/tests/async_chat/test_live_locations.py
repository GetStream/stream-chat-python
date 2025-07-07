import datetime
from typing import Dict

import pytest

from stream_chat.async_chat.client import StreamChatAsync


@pytest.mark.incremental
class TestLiveLocations:
    @pytest.fixture(autouse=True)
    @pytest.mark.asyncio
    async def setup_channel_for_shared_locations(self, channel):
        await channel.update_partial(
            {"config_overrides": {"shared_locations": True}},
        )
        yield
        await channel.update_partial(
            {"config_overrides": {"shared_locations": False}},
        )

    async def test_get_user_locations(
        self, client: StreamChatAsync, channel, random_user: Dict
    ):
        # Create a message to attach location to
        now = datetime.datetime.now(datetime.timezone.utc)
        one_hour_later = now + datetime.timedelta(hours=1)
        shared_location = {
            "created_by_device_id": "test_device_id",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "end_at": one_hour_later.isoformat(),
        }

        channel.send_message(
            {"text": "Message with location", "shared_location": shared_location},
            random_user["id"],
        )

        # Get user locations
        response = await client.get_user_locations(random_user["id"])

        assert "active_live_locations" in response
        assert isinstance(response["active_live_locations"], list)

    async def test_update_user_location(
        self, client: StreamChatAsync, channel, random_user: Dict
    ):
        # Create a message to attach location to
        now = datetime.datetime.now(datetime.timezone.utc)
        one_hour_later = now + datetime.timedelta(hours=1)
        shared_location = {
            "created_by_device_id": "test_device_id",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "end_at": one_hour_later.isoformat(),
        }

        msg = await channel.send_message(
            {"text": "Message with location", "shared_location": shared_location},
            random_user["id"],
        )
        message_id = msg["message"]["id"]

        # Update user location
        location_data = {
            "created_by_device_id": "test_device_id",
            "latitude": 37.7749,
            "longitude": -122.4194,
        }
        response = await client.update_user_location(
            random_user["id"], message_id, location_data
        )

        assert response["latitude"] == location_data["latitude"]
        assert response["longitude"] == location_data["longitude"]

        # Get user locations to verify
        locations_response = await client.get_user_locations(random_user["id"])
        assert "active_live_locations" in locations_response
        assert len(locations_response["active_live_locations"]) > 0
        location = locations_response["active_live_locations"][0]
        assert location["latitude"] == location_data["latitude"]
        assert location["longitude"] == location_data["longitude"]
