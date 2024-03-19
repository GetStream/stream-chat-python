from typing import Dict, List, Optional

from stream_chat.base.segment import SegmentInterface
from stream_chat.types.base import SortParam
from stream_chat.types.segment import (
    QuerySegmentTargetsOptions,
    SegmentData,
    SegmentUpdatableFields,
)
from stream_chat.types.stream_response import StreamResponse


class Segment(SegmentInterface):
    def create(
        self, segment_id: Optional[str] = None, data: Optional[SegmentData] = None
    ) -> StreamResponse:
        if segment_id is not None:
            self.segment_id = segment_id
        if data is not None:
            self.data = data

        state = self.client.create_segment(
            segment_type=self.segment_type, segment_id=self.segment_id, data=self.data
        )

        if self.segment_id is None and state.is_ok() and "segment" in state:  # type: ignore
            self.segment_id = state["segment"]["id"]  # type: ignore
        return state  # type: ignore

    def get(self) -> StreamResponse:
        super().verify_segment_id()
        return self.client.get_segment(segment_id=self.segment_id)  # type: ignore

    def update(self, data: SegmentUpdatableFields) -> StreamResponse:
        super().verify_segment_id()
        return self.client.update_segment(  # type: ignore
            segment_id=self.segment_id, data=data
        )

    def delete(self) -> StreamResponse:
        super().verify_segment_id()
        return self.client.delete_segment(segment_id=self.segment_id)  # type: ignore

    def target_exists(self, target_id: str) -> StreamResponse:
        super().verify_segment_id()
        return self.client.segment_target_exists(  # type: ignore
            segment_id=self.segment_id, target_id=target_id
        )

    def add_targets(self, target_ids: list) -> StreamResponse:
        super().verify_segment_id()
        return self.client.add_segment_targets(  # type: ignore
            segment_id=self.segment_id, target_ids=target_ids
        )

    def query_targets(
        self,
        filter_conditions: Optional[Dict] = None,
        sort: Optional[List[SortParam]] = None,
        options: Optional[QuerySegmentTargetsOptions] = None,
    ) -> StreamResponse:
        super().verify_segment_id()
        return self.client.query_segment_targets(  # type: ignore
            segment_id=self.segment_id,
            sort=sort,
            filter_conditions=filter_conditions,
            options=options,
        )

    def remove_targets(self, target_ids: list) -> StreamResponse:
        super().verify_segment_id()
        return self.client.remove_segment_targets(  # type: ignore
            segment_id=self.segment_id, target_ids=target_ids
        )
