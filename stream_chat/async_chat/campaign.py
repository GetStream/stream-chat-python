import datetime
from typing import Any, Optional, Union

from stream_chat.base.campaign import CampaignInterface
from stream_chat.types.campaign import CampaignData
from stream_chat.types.stream_response import StreamResponse


class Campaign(CampaignInterface):

    async def create(self) -> StreamResponse:
        state = await self.client.create_campaign(campaign_id=self.campaign_id, data=self.data)

        if self.campaign_id is None and state.is_ok() and "campaign" in state:
            self.campaign_id = state["campaign"]["id"]
        return state

    async def get(self) -> StreamResponse:
        return await self.client.get_campaign(campaign_id=self.campaign_id)

    async def update(self, data: CampaignData) -> StreamResponse:
        return await self.client.update_campaign(campaign_id=self.campaign_id, data=data)

    async def delete(self, **options: Any) -> StreamResponse:
        return await self.client.delete_campaign(campaign_id=self.campaign_id, options=options)

    async def start(self, scheduled_for: Optional[Union[str, datetime.datetime]] = None) -> StreamResponse:
        return await self.client.start_campaign(campaign_id=self.campaign_id, scheduled_for=scheduled_for)

    async def stop(self) -> StreamResponse:
        return await self.client.stop_campaign(campaign_id=self.campaign_id)