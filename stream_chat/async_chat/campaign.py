import datetime
from typing import Any, Optional, Union

from stream_chat.base.campaign import CampaignInterface
from stream_chat.types.campaign import CampaignData
from stream_chat.types.stream_response import StreamResponse


class Campaign(CampaignInterface):
    async def create(
        self, campaign_id: Optional[str] = None, data: Optional[CampaignData] = None
    ) -> StreamResponse:
        if campaign_id is not None:
            self.campaign_id = campaign_id
        if data is not None:
            self.data = data
        state = await self.client.create_campaign(  # type: ignore
            campaign_id=self.campaign_id, data=self.data
        )

        if self.campaign_id is None and state.is_ok() and "campaign" in state:
            self.campaign_id = state["campaign"]["id"]
        return state

    async def get(self) -> StreamResponse:
        return await self.client.get_campaign(  # type: ignore
            campaign_id=self.campaign_id
        )

    async def update(self, data: CampaignData) -> StreamResponse:
        return await self.client.update_campaign(  # type: ignore
            campaign_id=self.campaign_id, data=data
        )

    async def delete(self, **options: Any) -> StreamResponse:
        return await self.client.delete_campaign(  # type: ignore
            campaign_id=self.campaign_id, **options
        )

    async def start(
        self,
        scheduled_for: Optional[Union[str, datetime.datetime]] = None,
        stop_at: Optional[Union[str, datetime.datetime]] = None,
    ) -> StreamResponse:
        return await self.client.start_campaign(  # type: ignore
            campaign_id=self.campaign_id, scheduled_for=scheduled_for, stop_at=stop_at
        )

    async def stop(self) -> StreamResponse:
        return await self.client.stop_campaign(  # type: ignore
            campaign_id=self.campaign_id
        )
