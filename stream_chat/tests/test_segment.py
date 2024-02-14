import uuid

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
        assert "segment" in received
        assert "id" in received["segment"]
        assert "name" in received["segment"]
        assert received["segment"]["name"] == created["segment"]["name"]

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

    def test_segment_targets(self, client: StreamChat):
        segment = client.segment(segment_type=SegmentType.USER)
        created = segment.create()
        assert created.is_ok()
        assert "segment" in created
        assert "id" in created["segment"]
        assert "name" in created["segment"]

        target_id = str(uuid.uuid4())
        target_added = segment.add_targets(target_ids=[target_id])
        assert target_added.is_ok()

        target_exists = segment.target_exists(target_id=target_id)
        assert target_exists.is_ok()

        target_deleted = segment.delete_targets(target_ids=[target_id])
        assert target_deleted.is_ok()

        deleted = segment.delete()
        assert deleted.is_ok()

