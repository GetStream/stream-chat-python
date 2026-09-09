from unittest.mock import AsyncMock, MagicMock

import pytest

from stream_chat.async_chat.channel import Channel as AsyncChannel
from stream_chat.channel import Channel


def test_delete_omits_skip_truncate_by_default() -> None:
    client = MagicMock()
    Channel(client, "messaging", "chan").delete()
    client.delete.assert_called_once_with(
        "channels/messaging/chan", params={"hard_delete": False}
    )


def test_delete_sends_skip_truncate() -> None:
    client = MagicMock()
    Channel(client, "messaging", "chan").delete(skip_truncate=True)
    client.delete.assert_called_once_with(
        "channels/messaging/chan", params={"hard_delete": False, "skip_truncate": True}
    )


@pytest.mark.asyncio
async def test_async_delete_sends_skip_truncate() -> None:
    client = MagicMock()
    client.delete = AsyncMock()
    await AsyncChannel(client, "messaging", "chan").delete(skip_truncate=True)
    client.delete.assert_called_once_with(
        "channels/messaging/chan", {"hard_delete": False, "skip_truncate": True}
    )
