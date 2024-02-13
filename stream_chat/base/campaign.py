import abc
from typing import Awaitable, Dict, List, Union, Optional

from stream_chat.base.client import StreamChatInterface
from stream_chat.types.campaign import CampaignData
from stream_chat.types.stream_response import StreamResponse


class CampaignInterface(abc.ABC):
    def __init__(
        self,
        client: StreamChatInterface,
        campaign_id: Optional[str] = None,
        data: CampaignData = None,
    ):
        self.client = client
        self.campaign_id = campaign_id
        self.data = data

    @abc.abstractmethod
    def create(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def get(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def start(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def stop(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass
