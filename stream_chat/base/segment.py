import abc
from typing import Optional, Awaitable, Union, List

from stream_chat.base.client import StreamChatInterface
from stream_chat.types.segment import SegmentType, SegmentData
from stream_chat.types.stream_response import StreamResponse


class SegmentInterface(abc.ABC):
    def __init__(
        self,
        client: StreamChatInterface,
        segment_type: SegmentType,
        segment_id: Optional[str] = None,
        data: Optional[SegmentData] = None,
    ):
        self.segment_type = segment_type
        self.segment_id = segment_id
        self.client = client
        self.data = data

    @abc.abstractmethod
    def create(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def get(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update(self, data: SegmentData) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def target_exists(self, target_id: str) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def add_targets(self, target_ids: List[str]) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete_targets(self, target_ids: List[str]) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass
