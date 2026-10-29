import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from stream_chat import StreamChat
from stream_chat.async_chat import StreamChatAsync
from stream_chat.async_chat.channel import Channel as AsyncChannel
from stream_chat.channel import Channel
from stream_chat.types.scheduled_messages import format_scheduled_at

CET = datetime.timezone(datetime.timedelta(hours=1))


def _sync_client() -> StreamChat:
    client = StreamChat(api_key="key", api_secret="secret")
    client.post = MagicMock()  # type: ignore[method-assign]
    client.patch = MagicMock()  # type: ignore[method-assign]
    client.delete = MagicMock()  # type: ignore[method-assign]
    return client


def test_format_scheduled_at() -> None:
    assert (
        format_scheduled_at(datetime.datetime(2030, 1, 2, 4, 4, 5, tzinfo=CET))
        == "2030-01-02T03:04:05+00:00"
    )
    assert (
        format_scheduled_at(datetime.datetime(2030, 1, 2, 3, 4, 5))
        == "2030-01-02T03:04:05+00:00"
    )
    assert format_scheduled_at("2030-01-02T03:04:05Z") == "2030-01-02T03:04:05Z"


def test_send_message_with_scheduled_at() -> None:
    client = MagicMock()
    Channel(client, "messaging", "chan").send_message(
        {"text": "later"},
        "user-1",
        scheduled_at=datetime.datetime(2030, 1, 2, 4, 4, 5, tzinfo=CET),
    )
    client.post.assert_called_once_with(
        "channels/messaging/chan/message",
        data={
            "message": {"text": "later", "user": {"id": "user-1"}},
            "scheduled_at": "2030-01-02T03:04:05+00:00",
        },
    )


def test_send_message_without_scheduled_at() -> None:
    client = MagicMock()
    Channel(client, "messaging", "chan").send_message({"text": "now"}, "user-1")
    client.post.assert_called_once_with(
        "channels/messaging/chan/message",
        data={"message": {"text": "now", "user": {"id": "user-1"}}},
    )


def test_update_scheduled_message() -> None:
    client = _sync_client()
    client.update_scheduled_message(
        "sm-1",
        message={"text": "edited"},
        scheduled_at=datetime.datetime(2030, 1, 2, 3, 4, 5),
    )
    client.patch.assert_called_once_with(
        "scheduled_messages/sm-1",
        data={
            "message": {"text": "edited"},
            "scheduled_at": "2030-01-02T03:04:05+00:00",
        },
    )


def test_update_scheduled_message_only_time() -> None:
    client = _sync_client()
    client.update_scheduled_message("sm-1", scheduled_at="2030-01-02T03:04:05Z")
    client.patch.assert_called_once_with(
        "scheduled_messages/sm-1", data={"scheduled_at": "2030-01-02T03:04:05Z"}
    )


def test_update_scheduled_message_requires_a_change() -> None:
    client = _sync_client()
    with pytest.raises(ValueError):
        client.update_scheduled_message("sm-1")
    client.patch.assert_not_called()


def test_delete_scheduled_message() -> None:
    client = _sync_client()
    client.delete_scheduled_message("sm-1")
    client.delete.assert_called_once_with("scheduled_messages/sm-1")


def test_send_scheduled_message_now() -> None:
    client = _sync_client()
    client.send_scheduled_message_now("sm-1")
    client.post.assert_called_once_with("scheduled_messages/sm-1/send_now")


def test_query_scheduled_messages() -> None:
    client = _sync_client()
    client.query_scheduled_messages(
        "user-1",
        filter={"cid": "messaging:chan", "status": ["scheduled", "failed"]},
        sort=[{"field": "scheduled_at", "direction": 1}],
        options={"limit": 100, "next": "cursor"},
    )
    client.post.assert_called_once_with(
        "scheduled_messages/query",
        data={
            "user_id": "user-1",
            "filter": {"cid": "messaging:chan", "status": ["scheduled", "failed"]},
            "sort": [{"field": "scheduled_at", "direction": 1}],
            "limit": 100,
            "next": "cursor",
        },
    )


def test_query_scheduled_messages_minimal() -> None:
    client = _sync_client()
    client.query_scheduled_messages("user-1")
    client.post.assert_called_once_with(
        "scheduled_messages/query", data={"user_id": "user-1"}
    )


@pytest.mark.asyncio
async def test_async_send_message_with_scheduled_at() -> None:
    client = MagicMock()
    client.post = AsyncMock()
    await AsyncChannel(client, "messaging", "chan").send_message(
        {"text": "later"}, "user-1", scheduled_at="2030-01-02T03:04:05Z"
    )
    client.post.assert_called_once_with(
        "channels/messaging/chan/message",
        data={
            "message": {"text": "later", "user": {"id": "user-1"}},
            "scheduled_at": "2030-01-02T03:04:05Z",
        },
    )


@pytest.mark.asyncio
async def test_async_scheduled_message_calls() -> None:
    async with StreamChatAsync(api_key="key", api_secret="secret") as client:
        client.post = AsyncMock()  # type: ignore[method-assign]
        client.patch = AsyncMock()  # type: ignore[method-assign]
        client.delete = AsyncMock()  # type: ignore[method-assign]

        await client.update_scheduled_message("sm-1", message={"text": "edited"})
        client.patch.assert_called_once_with(
            "scheduled_messages/sm-1", data={"message": {"text": "edited"}}
        )

        await client.delete_scheduled_message("sm-1")
        client.delete.assert_called_once_with("scheduled_messages/sm-1")

        await client.send_scheduled_message_now("sm-1")
        client.post.assert_called_once_with("scheduled_messages/sm-1/send_now")

        client.post.reset_mock()
        await client.query_scheduled_messages(
            "user-1", filter={"cid": "messaging:chan"}, options={"limit": 10}
        )
        client.post.assert_called_once_with(
            "scheduled_messages/query",
            data={
                "user_id": "user-1",
                "filter": {"cid": "messaging:chan"},
                "limit": 10,
            },
        )

        with pytest.raises(ValueError):
            await client.update_scheduled_message("sm-1")
