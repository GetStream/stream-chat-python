from stream_chat.base.segment import SegmentInterface
from stream_chat.types.segment import SegmentData
from stream_chat.types.stream_response import StreamResponse


class Segment(SegmentInterface):

    def create(self) -> StreamResponse:
        state = self.client.create_segment(
            segment_type=self.segment_type,
            segment_id=self.segment_id,
            data=self.data
        )

        if self.segment_id is None and state.is_ok() and "segment" in state:
            self.segment_id = state["segment"]["id"]
        return state

    def get(self) -> StreamResponse:
        return self.client.get_segment(segment_id=self.segment_id)

    def update(self, data: SegmentData) -> StreamResponse:
        return self.client.update_segment(
            segment_id=self.segment_id,
            data=data
        )

    def delete(self) -> StreamResponse:
        return self.client.delete_segment(segment_id=self.segment_id)

    def target_exists(self, target_id: str) -> StreamResponse:
        return self.client.segment_target_exists(segment_id=self.segment_id, target_id=target_id)

    def add_targets(self, target_ids: list) -> StreamResponse:
        return self.client.add_segment_targets(segment_id=self.segment_id, target_ids=target_ids)

    def delete_targets(self, target_ids: list) -> StreamResponse:
        return self.client.delete_segment_targets(segment_id=self.segment_id, target_ids=target_ids)