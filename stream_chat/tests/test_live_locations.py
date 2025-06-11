import pytest
from typing import Dict

from stream_chat import StreamChat


@pytest.mark.incremental
class TestLiveLocations:
    def test_get_user_locations(self, client: StreamChat, random_user: Dict):
        # First create a message to attach location to
        channel = client.channel("messaging", str(random_user["id"]))
        channel.create(random_user["id"])

        # Create a message to attach location to
        shared_location = {
            "latitude": 37.7749,
            "longitude": -122.4194,
        }

        channel.send_message(
            {"text": "Message with location", "shared_location": shared_location},
            random_user["id"],
        )

        # Get user locations
        response = client.get_user_locations(random_user["id"])

        assert "active_live_locations" in response
        assert isinstance(response["active_live_locations"], list)

    def test_update_user_location(self, client: StreamChat, random_user: Dict):
        # First create a message to attach location to
        channel = client.channel("messaging", str(random_user["id"]))
        channel.create(random_user["id"])

        # Create a message to attach location to
        shared_location = {
            "latitude": 37.7749,
            "longitude": -122.4194,
        }

        msg = channel.send_message(
            {"text": "Message with location", "shared_location": shared_location},
            random_user["id"],
        )
        message_id = msg["message"]["id"]

        # Update user location
        location_data = {
            "latitude": 37.7749,
            "longitude": -122.4194,
        }
        response = client.update_user_location(message_id, location_data)

        assert "shared_location" in response
        assert response["shared_location"]["latitude"] == location_data["latitude"]
        assert response["shared_location"]["longitude"] == location_data["longitude"]

        # Get user locations to verify
        locations_response = client.get_user_locations(random_user["id"])
        assert "active_live_locations" in locations_response
        assert len(locations_response["active_live_locations"]) > 0
        location = locations_response["active_live_locations"][0]
        assert location["latitude"] == location_data["latitude"]
        assert location["longitude"] == location_data["longitude"]

        # Cleanup
        try:
            channel.delete()
        except Exception:
            pass
