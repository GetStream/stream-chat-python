import datetime
from typing import Dict

import pytest

from stream_chat import StreamChat
from stream_chat.types.segment import SegmentType


@pytest.mark.incremental
class TestCampaign:
    def test_campaign_crud(self, client: StreamChat, random_user: Dict):
        segment = client.create_segment(segment_type=SegmentType.USER)
        segment_id = segment["segment"]["id"]

        sender_id = random_user["id"]

        campaign = client.campaign(
            data={
                "message_template": {
                    "text": "{Hello}",
                },
                "segment_ids": [segment_id],
                "sender_id": sender_id,
                "name": "some name",
            }
        )
        created = campaign.create(
            data={
                "name": "created name",
            }
        )
        assert created.is_ok()
        assert "campaign" in created
        assert "id" in created["campaign"]
        assert "name" in created["campaign"]
        assert created["campaign"]["name"] == "created name"

        received = campaign.get()
        assert received.is_ok()
        assert "campaign" in received
        assert "id" in received["campaign"]
        assert "name" in received["campaign"]
        assert received["campaign"]["name"] == created["campaign"]["name"]

        updated = campaign.update(
            {
                "message_template": {
                    "text": "{Hello}",
                },
                "segment_ids": [segment_id],
                "sender_id": sender_id,
                "name": "updated_name",
            }
        )
        assert updated.is_ok()
        assert "campaign" in updated
        assert "id" in updated["campaign"]
        assert "name" in updated["campaign"]
        assert updated["campaign"]["name"] == "updated_name"

        deleted = campaign.delete()
        assert deleted.is_ok()

        client.delete_segment(segment_id=segment_id)

    def test_campaign_start_stop(self, client: StreamChat, random_user: Dict):
        segment = client.create_segment(segment_type=SegmentType.USER)
        segment_id = segment["segment"]["id"]

        sender_id = random_user["id"]

        target_added = client.add_segment_targets(
            segment_id=segment_id, target_ids=[sender_id]
        )
        assert target_added.is_ok()

        campaign = client.campaign(
            data={
                "message_template": {
                    "text": "{Hello}",
                },
                "segment_ids": [segment_id],
                "sender_id": sender_id,
                "name": "some name",
            }
        )
        created = campaign.create()
        assert created.is_ok()
        assert "campaign" in created
        assert "id" in created["campaign"]
        assert "name" in created["campaign"]

        now = datetime.datetime.now(datetime.timezone.utc)
        one_hour_later = now + datetime.timedelta(hours=1)

        started = campaign.start(scheduled_for=one_hour_later)
        assert started.is_ok()
        assert "campaign" in started
        assert "id" in started["campaign"]
        assert "name" in started["campaign"]

        stopped = campaign.stop()
        assert stopped.is_ok()
        assert "campaign" in stopped
        assert "id" in stopped["campaign"]
        assert "name" in stopped["campaign"]

        deleted = campaign.delete()
        assert deleted.is_ok()

        client.delete_segment(segment_id=segment_id)
