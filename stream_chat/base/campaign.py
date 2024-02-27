import abc
import datetime
from typing import Awaitable, Optional, Union

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
    def create(
        self, campaign_id: Optional[str], data: Optional[CampaignData]
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def get(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def update(
        self, data: CampaignData
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def delete(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def start(
        self,
        scheduled_for: Optional[Union[str, datetime.datetime]] = None,
        stop_at: Optional[Union[str, datetime.datetime]] = None,
    ) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass

    @abc.abstractmethod
    def stop(self) -> Union[StreamResponse, Awaitable[StreamResponse]]:
        pass
