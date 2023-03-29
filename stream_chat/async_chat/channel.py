import json
from typing import Any, Dict, Iterable, List, Union

from stream_chat.base.channel import ChannelInterface, add_user_id
from stream_chat.types.stream_response import StreamResponse


class Channel(ChannelInterface):
    async def send_message(
        self, message: Dict, user_id: str, **options: Any
    ) -> StreamResponse:
        payload = {"message": add_user_id(message, user_id), **options}
        return await self.client.post(f"{self.url}/message", data=payload)

    async def get_messages(self, message_ids: List[str]) -> StreamResponse:
        return await self.client.get(
            f"{self.url}/messages", params={"ids": ",".join(message_ids)}
        )

    async def send_event(self, event: Dict, user_id: str) -> StreamResponse:
        payload = {"event": add_user_id(event, user_id)}
        return await self.client.post(f"{self.url}/event", data=payload)

    async def send_reaction(
        self, message_id: str, reaction: Dict, user_id: str
    ) -> StreamResponse:
        payload = {"reaction": add_user_id(reaction, user_id)}
        return await self.client.post(f"messages/{message_id}/reaction", data=payload)

    async def delete_reaction(
        self, message_id: str, reaction_type: str, user_id: str
    ) -> StreamResponse:
        return await self.client.delete(
            f"messages/{message_id}/reaction/{reaction_type}",
            params={"user_id": user_id},
        )

    async def create(self, user_id: str, **options: Any) -> StreamResponse:
        self.custom_data["created_by"] = {"id": user_id}
        options["watch"] = False
        options["state"] = False
        options["presence"] = False
        return await self.query(**options)

    async def query(self, **options: Any) -> StreamResponse:
        payload = {"state": True, "data": self.custom_data, **options}

        url = f"channels/{self.channel_type}"
        if self.id is not None:
            url = f"{url}/{self.id}"

        state = await self.client.post(f"{url}/query", data=payload)

        if self.id is None:
            self.id = state["channel"]["id"]

        return state

    async def query_members(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> List[Dict]:
        payload = {
            "id": self.id,
            "type": self.channel_type,
            "filter_conditions": filter_conditions,
            "sort": self.client.normalize_sort(sort),
            **options,
        }
        response: StreamResponse = await self.client.get(
            "members", params={"payload": json.dumps(payload)}
        )
        return response["members"]

    async def update(
        self, channel_data: Dict, update_message: Dict = None
    ) -> StreamResponse:
        payload = {"data": channel_data, "message": update_message}
        return await self.client.post(self.url, data=payload)

    async def update_partial(
        self, to_set: Dict = None, to_unset: Iterable[str] = None
    ) -> StreamResponse:
        payload = {"set": to_set or {}, "unset": to_unset or []}
        return await self.client.patch(self.url, data=payload)

    async def delete(self) -> StreamResponse:
        return await self.client.delete(self.url)

    async def truncate(self, **options: Any) -> StreamResponse:
        return await self.client.post(f"{self.url}/truncate", data=options)

    async def add_members(
        self, members: Iterable[Dict], message: Dict = None, **options: Any
    ) -> StreamResponse:
        payload = {"add_members": members, "message": message, **options}
        return await self.client.post(self.url, data=payload)

    async def assign_roles(
        self, members: Iterable[Dict], message: Dict = None
    ) -> StreamResponse:
        return await self.client.post(
            self.url, data={"assign_roles": members, "message": message}
        )

    async def invite_members(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return await self.client.post(
            self.url, data={"invites": user_ids, "message": message}
        )

    async def add_moderators(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return await self.client.post(
            self.url, data={"add_moderators": user_ids, "message": message}
        )

    async def remove_members(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return await self.client.post(
            self.url, data={"remove_members": user_ids, "message": message}
        )

    async def demote_moderators(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return await self.client.post(
            self.url, data={"demote_moderators": user_ids, "message": message}
        )

    async def mark_read(self, user_id: str, **data: Any) -> StreamResponse:
        payload = add_user_id(data, user_id)
        return await self.client.post(f"{self.url}/read", data=payload)

    async def get_replies(self, parent_id: str, **options: Any) -> StreamResponse:
        return await self.client.get(f"messages/{parent_id}/replies", params=options)

    async def get_reactions(self, message_id: str, **options: Any) -> StreamResponse:
        return await self.client.get(f"messages/{message_id}/reactions", params=options)

    async def ban_user(self, target_id: str, **options: Any) -> StreamResponse:
        return await self.client.ban_user(  # type: ignore
            target_id, type=self.channel_type, id=self.id, **options
        )

    async def unban_user(self, target_id: str, **options: Any) -> StreamResponse:
        return await self.client.unban_user(  # type: ignore
            target_id, type=self.channel_type, id=self.id, **options
        )

    async def accept_invite(self, user_id: str, **data: Any) -> StreamResponse:
        payload = add_user_id(data, user_id)
        payload["accept_invite"] = True
        response = await self.client.post(self.url, data=payload)
        self.custom_data = response["channel"]
        return response

    async def reject_invite(self, user_id: str, **data: Any) -> StreamResponse:
        payload = add_user_id(data, user_id)
        payload["reject_invite"] = True
        response = await self.client.post(self.url, data=payload)
        self.custom_data = response["channel"]
        return response

    async def send_file(
        self, url: str, name: str, user: Dict, content_type: str = None
    ) -> StreamResponse:
        return await self.client.send_file(  # type: ignore
            f"{self.url}/file", url, name, user, content_type=content_type
        )

    async def send_image(
        self, url: str, name: str, user: Dict, content_type: str = None
    ) -> StreamResponse:
        return await self.client.send_file(  # type: ignore
            f"{self.url}/image", url, name, user, content_type=content_type
        )

    async def delete_file(self, url: str) -> StreamResponse:
        return await self.client.delete(f"{self.url}/file", {"url": url})

    async def delete_image(self, url: str) -> StreamResponse:
        return await self.client.delete(f"{self.url}/image", {"url": url})

    async def hide(self, user_id: str) -> StreamResponse:
        return await self.client.post(f"{self.url}/hide", data={"user_id": user_id})

    async def show(self, user_id: str) -> StreamResponse:
        return await self.client.post(f"{self.url}/show", data={"user_id": user_id})

    async def mute(self, user_id: str, expiration: int = None) -> StreamResponse:
        params: Dict[str, Union[str, int]] = {
            "user_id": user_id,
            "channel_cid": self.cid,
        }
        if expiration:
            params["expiration"] = expiration
        return await self.client.post("moderation/mute/channel", data=params)

    async def unmute(self, user_id: str) -> StreamResponse:
        params = {
            "user_id": user_id,
            "channel_cid": self.cid,
        }
        return await self.client.post("moderation/unmute/channel", data=params)
