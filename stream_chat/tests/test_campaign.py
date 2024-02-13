import pytest

from stream_chat import StreamChat
from stream_chat.types.segment import SegmentType


@pytest.mark.incremental
class TestCampaign:
    def test_campaign_crud(self, client: StreamChat):
        segment = client.create_segment(segment_type=SegmentType.USER, segment_name="test_segment")
        segment_id = segment["segment"]["id"]

        sender_id = "test-regular-user"

        campaign = client.campaign(data={
            "message_template": {
                "text": "{Hello}",
            },
            "segment_ids": [segment_id],
            "sender_id": sender_id,
            "name": "some name",
        })
        created = campaign.create()
        assert created.is_ok()
        assert "campaign" in created
        assert "id" in created["campaign"]
        assert "name" in created["campaign"]

        client.delete_segment(segment_id=segment_id)

