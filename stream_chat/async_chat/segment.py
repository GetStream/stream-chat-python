from typing import Optional

from stream_chat.base.segment import SegmentInterface
from stream_chat.types.segment import QuerySegmentTargetsOptions, SegmentData
from stream_chat.types.stream_response import StreamResponse


class Segment(SegmentInterface):

    async def create(
        self, segment_id: Optional[str] = None, data: Optional[SegmentData] = None
    ) -> StreamResponse:
        if segment_id is not None:
            self.segment_id = segment_id
        if data is not None:
            self.data = data

        state = await self.client.create_segment(  # type: ignore
            segment_type=self.segment_type, segment_id=self.segment_id, data=self.data
        )

        if self.segment_id is None and state.is_ok() and "segment" in state:
            self.segment_id = state["segment"]["id"]
        return state

    async def get(self) -> StreamResponse:
        return await self.client.get_segment(segment_id=self.segment_id)  # type: ignore

    async def update(self, data: SegmentData) -> StreamResponse:
        return await self.client.update_segment(  # type: ignore
            segment_id=self.segment_id, data=data
        )

    async def delete(self) -> StreamResponse:
        return await self.client.delete_segment(  # type: ignore
            segment_id=self.segment_id
        )

    async def target_exists(self, target_id: str) -> StreamResponse:
        return await self.client.segment_target_exists(  # type: ignore
            segment_id=self.segment_id, target_id=target_id
        )

    async def add_targets(self, target_ids: list) -> StreamResponse:
        return await self.client.add_segment_targets(  # type: ignore
            segment_id=self.segment_id, target_ids=target_ids
        )

    async def query_targets(
        self, options: QuerySegmentTargetsOptions
    ) -> StreamResponse:
        return await self.client.query_segment_targets(  # type: ignore
            segment_id=self.segment_id, options=options
        )

    async def delete_targets(self, target_ids: list) -> StreamResponse:
        return await self.client.delete_segment_targets(  # type: ignore
            segment_id=self.segment_id, target_ids=target_ids
        )
