import uuid

from stream_chat.base.segment import SegmentInterface
from stream_chat.types.segment import UpdateSegmentData
from stream_chat.types.stream_response import StreamResponse


class Segment(SegmentInterface):

    def create(self) -> StreamResponse:
        if self.segment_name is None:
            self.segment_name = str(uuid.uuid4())

        state = self.client.create_segment(
            segment_type=self.segment_type,
            segment_id=self.segment_id,
            segment_name=self.segment_name,
            data=self.data
        )

        if self.segment_id is None and state.is_ok() and "segment" in state:
            self.segment_id = state["segment"]["id"]
        return state

    def get(self) -> StreamResponse:
        return self.client.query_segments(
            filter_conditions={
                "id": self.segment_id,
            },
            options={
                "limit": 1,
            }
        )

    def update(self, data: UpdateSegmentData) -> StreamResponse:
        return self.client.update_segment(
            segment_id=self.segment_id,
            data=data
        )

    def delete(self) -> StreamResponse:
        return self.client.delete_segment(segment_id=self.segment_id)
