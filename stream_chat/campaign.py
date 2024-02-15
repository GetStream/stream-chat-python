import datetime
from typing import Any, Optional, Union

from stream_chat.base.campaign import CampaignInterface
from stream_chat.types.campaign import CampaignData
from stream_chat.types.stream_response import StreamResponse


class Campaign(CampaignInterface):

    def create(self, campaign_id: Optional[str] = None, data: Optional[CampaignData] = None) -> StreamResponse:
        if campaign_id is not None:
            self.campaign_id = campaign_id
        if data is not None:
            self.data = data
        state = self.client.create_campaign(campaign_id=self.campaign_id, data=self.data)

        if self.campaign_id is None and state.is_ok() and "campaign" in state:
            self.campaign_id = state["campaign"]["id"]
        return state

    def get(self) -> StreamResponse:
        return self.client.get_campaign(campaign_id=self.campaign_id)

    def update(self, data: CampaignData) -> StreamResponse:
        return self.client.update_campaign(campaign_id=self.campaign_id, data=data)

    def delete(self, **options: Any) -> StreamResponse:
        return self.client.delete_campaign(campaign_id=self.campaign_id, **options)

    def start(self, scheduled_for: Optional[Union[str, datetime.datetime]] = None) -> StreamResponse:
        return self.client.start_campaign(campaign_id=self.campaign_id, scheduled_for=scheduled_for)

    def stop(self) -> StreamResponse:
        return self.client.stop_campaign(campaign_id=self.campaign_id)
