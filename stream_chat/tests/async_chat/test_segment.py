import uuid

import pytest

from stream_chat.async_chat.client import StreamChatAsync
from stream_chat.types.segment import SegmentType


@pytest.mark.incremental
class TestSegment:
    async def test_segment_crud(self, client: StreamChatAsync):
        segment = client.segment(
            SegmentType.USER,
            data={
                "name": "test_segment",
                "description": "test_description",
            },
        )
        created = await segment.create()
        assert created.is_ok()
        assert "segment" in created
        assert "id" in created["segment"]
        assert "name" in created["segment"]

        received = await segment.get()
        assert received.is_ok()
        assert "segment" in received
        assert "id" in received["segment"]
        assert "name" in received["segment"]
        assert received["segment"]["name"] == created["segment"]["name"]

        updated = await segment.update(
            {
                "name": "updated_name",
                "description": "updated_description",
            }
        )
        assert updated.is_ok()
        assert "segment" in updated
        assert "id" in updated["segment"]
        assert "name" in updated["segment"]
        assert updated["segment"]["name"] == "updated_name"
        assert updated["segment"]["description"] == "updated_description"

        deleted = await segment.delete()
        assert deleted.is_ok()

    async def test_segment_targets(self, client: StreamChatAsync):
        segment = client.segment(segment_type=SegmentType.USER)
        created = await segment.create()
        assert created.is_ok()
        assert "segment" in created
        assert "id" in created["segment"]
        assert "name" in created["segment"]

        target_ids = [str(uuid.uuid4()) for _ in range(10)]
        target_added = await segment.add_targets(target_ids=target_ids)
        assert target_added.is_ok()

        target_exists = await segment.target_exists(target_id=target_ids[0])
        assert target_exists.is_ok()

        query_targets_1 = await segment.query_targets(
            {
                "limit": 3,
            }
        )
        assert query_targets_1.is_ok()
        assert "targets" in query_targets_1
        assert "next" in query_targets_1
        assert len(query_targets_1["targets"]) == 3

        query_targets_2 = await segment.query_targets(
            {
                "limit": 3,
                "next": query_targets_1["next"],
            }
        )
        assert query_targets_2.is_ok()
        assert "targets" in query_targets_2
        assert "next" in query_targets_2
        assert len(query_targets_2["targets"]) == 3

        target_deleted = await segment.remove_targets(target_ids=target_ids)
        assert target_deleted.is_ok()

        deleted = await segment.delete()
        assert deleted.is_ok()
