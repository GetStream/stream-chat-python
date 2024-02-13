import pytest

from stream_chat import StreamChat
from stream_chat.types.segment import SegmentType


@pytest.mark.incremental
class TestSegment:
    def test_segment_crud(self, client: StreamChat):
        segment = client.segment(segment_type=SegmentType.USER)
        created = segment.create()
        assert created.is_ok()
        assert "segment" in created
        assert "id" in created["segment"]
        assert "name" in created["segment"]

        received = segment.get()
        assert received.is_ok()
        assert "segments" in received
        assert len(received["segments"]) == 1
        assert "id" in received["segments"][0]
        assert "name" in received["segments"][0]
        assert received["segments"][0]["name"] == created["segment"]["name"]

        updated = segment.update({
            "name": "updated_name"
        })
        assert updated.is_ok()
        assert "segment" in updated
        assert "id" in updated["segment"]
        assert "name" in updated["segment"]
        assert updated["segment"]["name"] == "updated_name"

        deleted = segment.delete()
        assert deleted.is_ok()

