import json
from typing import Any, Dict, Iterable, List, Optional, Union

from stream_chat.base.channel import ChannelInterface, add_user_id
from stream_chat.base.exceptions import StreamChannelException
from stream_chat.types.stream_response import StreamResponse


class Channel(ChannelInterface):
    def send_message(
        self, message: Dict, user_id: str, **options: Any
    ) -> StreamResponse:
        payload = {"message": add_user_id(message, user_id), **options}
        return self.client.post(f"{self.url}/message", data=payload)

    def send_event(self, event: Dict, user_id: str) -> StreamResponse:
        payload = {"event": add_user_id(event, user_id)}
        return self.client.post(f"{self.url}/event", data=payload)

    def send_reaction(
        self, message_id: str, reaction: Dict, user_id: str
    ) -> StreamResponse:
        payload = {"reaction": add_user_id(reaction, user_id)}
        return self.client.post(f"messages/{message_id}/reaction", data=payload)

    def delete_reaction(
        self, message_id: str, reaction_type: str, user_id: str
    ) -> StreamResponse:
        return self.client.delete(
            f"messages/{message_id}/reaction/{reaction_type}",
            params={"user_id": user_id},
        )

    def create(self, user_id: str, **options: Any) -> StreamResponse:
        self.custom_data["created_by"] = {"id": user_id}
        options["watch"] = False
        options["state"] = False
        options["presence"] = False
        return self.query(**options)

    def get_messages(self, message_ids: List[str]) -> StreamResponse:
        return self.client.get(
            f"{self.url}/messages", params={"ids": ",".join(message_ids)}
        )

    def query(self, **options: Any) -> StreamResponse:
        payload = {"state": True, "data": self.custom_data, **options}

        url = f"channels/{self.channel_type}"
        if self.id is not None:
            url = f"{url}/{self.id}"

        state = self.client.post(f"{url}/query", data=payload)

        if self.id is None:
            self.id: str = state["channel"]["id"]

        return state

    def query_members(
        self, filter_conditions: Dict, sort: List[Dict] = None, **options: Any
    ) -> List[Dict]:
        payload = {
            "id": self.id,
            "type": self.channel_type,
            "filter_conditions": filter_conditions,
            "sort": self.client.normalize_sort(sort),
            **options,
        }
        response: StreamResponse = self.client.get(
            "members", params={"payload": json.dumps(payload)}
        )
        return response["members"]

    def update(self, channel_data: Dict, update_message: Dict = None) -> StreamResponse:
        payload = {"data": channel_data, "message": update_message}
        return self.client.post(self.url, data=payload)

    def update_partial(
        self, to_set: Dict = None, to_unset: Iterable[str] = None
    ) -> StreamResponse:
        payload = {"set": to_set or {}, "unset": to_unset or []}
        return self.client.patch(self.url, data=payload)

    def delete(self, hard: bool = False) -> StreamResponse:
        return self.client.delete(self.url, params={"hard_delete": hard})

    def truncate(self, **options: Any) -> StreamResponse:
        return self.client.post(f"{self.url}/truncate", data=options)

    def add_members(
        self,
        members: Union[Iterable[Dict], Iterable[str]],
        message: Dict = None,
        **options: Any,
    ) -> StreamResponse:
        payload = {"add_members": members, "message": message, **options}
        return self.client.post(self.url, data=payload)

    def assign_roles(
        self, members: Iterable[Dict], message: Dict = None
    ) -> StreamResponse:
        return self.client.post(
            self.url, data={"assign_roles": members, "message": message}
        )

    def invite_members(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return self.client.post(
            self.url, data={"invites": user_ids, "message": message}
        )

    def add_moderators(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return self.client.post(
            self.url, data={"add_moderators": user_ids, "message": message}
        )

    def remove_members(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return self.client.post(
            self.url, data={"remove_members": user_ids, "message": message}
        )

    def demote_moderators(
        self, user_ids: Iterable[str], message: Dict = None
    ) -> StreamResponse:
        return self.client.post(
            self.url, data={"demote_moderators": user_ids, "message": message}
        )

    def mark_read(self, user_id: str, **data: Any) -> StreamResponse:
        payload = add_user_id(data, user_id)
        return self.client.post(f"{self.url}/read", data=payload)

    def mark_unread(self, user_id: str, **data: Any) -> StreamResponse:
        payload = add_user_id(data, user_id)
        return self.client.post(f"{self.url}/unread", data=payload)

    def get_replies(self, parent_id: str, **options: Any) -> StreamResponse:
        return self.client.get(f"messages/{parent_id}/replies", params=options)

    def get_reactions(self, message_id: str, **options: Any) -> StreamResponse:
        return self.client.get(f"messages/{message_id}/reactions", params=options)

    def ban_user(self, target_id: str, **options: Any) -> StreamResponse:
        return self.client.ban_user(  # type: ignore
            target_id, type=self.channel_type, id=self.id, **options
        )

    def unban_user(self, target_id: str, **options: Any) -> StreamResponse:
        return self.client.unban_user(  # type: ignore
            target_id, type=self.channel_type, id=self.id, **options
        )

    def accept_invite(self, user_id: str, **data: Any) -> StreamResponse:
        payload = add_user_id(data, user_id)
        payload["accept_invite"] = True
        response = self.client.post(self.url, data=payload)
        self.custom_data = response["channel"]
        return response

    def reject_invite(self, user_id: str, **data: Any) -> StreamResponse:
        payload = add_user_id(data, user_id)
        payload["reject_invite"] = True
        response = self.client.post(self.url, data=payload)
        self.custom_data = response["channel"]
        return response

    def send_file(
        self, url: str, name: str, user: Dict, content_type: str = None
    ) -> StreamResponse:
        return self.client.send_file(  # type: ignore
            f"{self.url}/file", url, name, user, content_type=content_type
        )

    def send_image(
        self, url: str, name: str, user: Dict, content_type: str = None
    ) -> StreamResponse:
        return self.client.send_file(  # type: ignore
            f"{self.url}/image", url, name, user, content_type=content_type
        )

    def delete_file(self, url: str) -> StreamResponse:
        return self.client.delete(f"{self.url}/file", {"url": url})

    def delete_image(self, url: str) -> StreamResponse:
        return self.client.delete(f"{self.url}/image", {"url": url})

    def hide(self, user_id: str) -> StreamResponse:
        return self.client.post(f"{self.url}/hide", data={"user_id": user_id})

    def show(self, user_id: str) -> StreamResponse:
        return self.client.post(f"{self.url}/show", data={"user_id": user_id})

    def mute(self, user_id: str, expiration: int = None) -> StreamResponse:
        params: Dict[str, Union[str, int]] = {
            "user_id": user_id,
            "channel_cid": self.cid,
        }
        if expiration:
            params["expiration"] = expiration
        return self.client.post("moderation/mute/channel", data=params)

    def unmute(self, user_id: str) -> StreamResponse:
        params = {
            "user_id": user_id,
            "channel_cid": self.cid,
        }
        return self.client.post("moderation/unmute/channel", data=params)

    def pin(self, user_id: str) -> StreamResponse:
        if not user_id:
            raise StreamChannelException("user_id must not be empty")

        payload = {"set": {"pinned": True}}
        return self.client.patch(f"{self.url}/member/{user_id}", data=payload)

    def unpin(self, user_id: str) -> StreamResponse:
        if not user_id:
            raise StreamChannelException("user_id must not be empty")

        payload = {"set": {"pinned": False}}
        return self.client.patch(f"{self.url}/member/{user_id}", data=payload)

    def archive(self, user_id: str) -> StreamResponse:
        if not user_id:
            raise StreamChannelException("user_id must not be empty")

        payload = {"set": {"archived": True}}
        return self.client.patch(f"{self.url}/member/{user_id}", data=payload)

    def unarchive(self, user_id: str) -> StreamResponse:
        if not user_id:
            raise StreamChannelException("user_id must not be empty")

        payload = {"set": {"archived": False}}
        return self.client.patch(f"{self.url}/member/{user_id}", data=payload)

    def update_member_partial(
        self, user_id: str, to_set: Dict = None, to_unset: Iterable[str] = None
    ) -> StreamResponse:
        if not user_id:
            raise StreamChannelException("user_id must not be empty")

        payload = {"set": to_set or {}, "unset": to_unset or []}
        return self.client.patch(f"{self.url}/member/{user_id}", data=payload)

    def create_draft(self, message: Dict, user_id: str) -> StreamResponse:
        message["user_id"] = user_id
        payload = {"message": message}
        return self.client.post(f"{self.url}/draft", data=payload)

    def delete_draft(
        self, user_id: str, parent_id: Optional[str] = None
    ) -> StreamResponse:
        params = {"user_id": user_id}
        if parent_id:
            params["parent_id"] = parent_id

        return self.client.delete(f"{self.url}/draft", params=params)

    def get_draft(
        self, user_id: str, parent_id: Optional[str] = None
    ) -> StreamResponse:
        params = {"user_id": user_id}
        if parent_id:
            params["parent_id"] = parent_id

        return self.client.get(f"{self.url}/draft", params=params)
