from stream_chat.base.campaign import CampaignInterface
from stream_chat.types.stream_response import StreamResponse


class Campaign(CampaignInterface):

    def create(self) -> StreamResponse:
        state = self.client.create_campaign(campaign_id=self.campaign_id, data=self.data)

        if self.campaign_id is None and state.is_ok() and "campaign" in state:
            self.campaign_id = state["campaign"]["id"]
        return state

    def get(self) -> StreamResponse:
        return self.client.get_campaign(campaign_id=self.campaign_id)

    def update(self, name: str = None, description: str = None) -> StreamResponse:
        payload = {"name": name, "description": description}
        return self.client.put(f"campaigns/{self.campaign_id}", data=payload)

    def delete(self) -> StreamResponse:
        return self.client.delete(f"campaigns/{self.campaign_id}")

    def start(self) -> StreamResponse:
        return self.client.get(f"campaigns/{self.campaign_id}")

    def stop(self) -> StreamResponse:
        return self.client.get(f"campaigns/{self.campaign_id}")

    def query(self) -> StreamResponse:
        return self.client.get(f"campaigns/{self.campaign_id}")
