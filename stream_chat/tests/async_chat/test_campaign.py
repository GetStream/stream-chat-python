import datetime
from typing import Dict

import pytest

from stream_chat import StreamChatAsync
from stream_chat.types.segment import SegmentType


@pytest.mark.incremental
class TestCampaign:
    async def test_campaign_crud(self, client: StreamChatAsync, random_user: Dict):
        segment = await client.create_segment(segment_type=SegmentType.USER)
        segment_id = segment["segment"]["id"]

        sender_id = random_user["id"]

        campaign = client.campaign(data={
            "message_template": {
                "text": "{Hello}",
            },
            "segment_ids": [segment_id],
            "sender_id": sender_id,
            "name": "some name",
        })
        created = await campaign.create()
        assert created.is_ok()
        assert "campaign" in created
        assert "id" in created["campaign"]
        assert "name" in created["campaign"]

        received = await campaign.get()
        assert received.is_ok()
        assert "campaign" in received
        assert "id" in received["campaign"]
        assert "name" in received["campaign"]
        assert received["campaign"]["name"] == created["campaign"]["name"]

        updated = await campaign.update({
            "message_template": {
                "text": "{Hello}",
            },
            "segment_ids": [segment_id],
            "sender_id": sender_id,
            "name": "updated_name",
        })
        assert updated.is_ok()
        assert "campaign" in updated
        assert "id" in updated["campaign"]
        assert "name" in updated["campaign"]
        assert updated["campaign"]["name"] == "updated_name"

        deleted = await campaign.delete()
        assert deleted.is_ok()

        await client.delete_segment(segment_id=segment_id)

    async def test_campaign_start_stop(self, client: StreamChatAsync, random_user: Dict):
        segment = await client.create_segment(segment_type=SegmentType.USER)
        segment_id = segment["segment"]["id"]

        sender_id = random_user["id"]

        target_added = await client.add_segment_targets(segment_id=segment_id, target_ids=[sender_id])
        assert target_added.is_ok()

        campaign = client.campaign(data={
            "message_template": {
                "text": "{Hello}",
            },
            "segment_ids": [segment_id],
            "sender_id": sender_id,
            "name": "some name",
        })
        created = await campaign.create()
        assert created.is_ok()
        assert "campaign" in created
        assert "id" in created["campaign"]
        assert "name" in created["campaign"]

        now = datetime.datetime.now(datetime.timezone.utc)
        one_hour_later = now + datetime.timedelta(hours=1)

        started = await campaign.start(scheduled_for=one_hour_later)
        assert started.is_ok()
        assert "campaign" in started
        assert "id" in started["campaign"]
        assert "name" in started["campaign"]

        stopped = await campaign.stop()
        assert stopped.is_ok()
        assert "campaign" in stopped
        assert "id" in stopped["campaign"]
        assert "name" in stopped["campaign"]

        deleted = await campaign.delete()
        assert deleted.is_ok()

        await client.delete_segment(segment_id=segment_id)
