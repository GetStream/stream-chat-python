from typing import Dict

import pytest

from stream_chat.async_chat import StreamChatAsync
from stream_chat.types.stream_response import StreamResponse


@pytest.mark.incremental
class TestQueryThreads:
    @pytest.mark.asyncio
    async def test_query_threads(
        self, client: StreamChatAsync, channel, random_user: Dict
    ):
        # Create a thread with some messages
        parent_message = await channel.send_message(
            {"text": "Parent message"}, random_user["id"]
        )
        thread_message = await channel.send_message(
            {"text": "Thread message", "parent_id": parent_message["message"]["id"]},
            random_user["id"],
        )

        # Query threads with filter and sort
        filter_conditions = {"parent_id": parent_message["message"]["id"]}
        sort_conditions = [{"field": "created_at", "direction": -1}]

        response = await client.query_threads(
            filter=filter_conditions, sort=sort_conditions, user_id=random_user["id"]
        )

        assert isinstance(response, StreamResponse)
        assert "threads" in response
        assert len(response["threads"]) > 0

        # Verify the thread message is in the response
        thread = response["threads"][0]
        assert "latest_replies" in thread
        assert len(thread["latest_replies"]) > 0
        assert thread["latest_replies"][0]["text"] == thread_message["message"]["text"]

    @pytest.mark.asyncio
    async def test_query_threads_with_options(
        self, client: StreamChatAsync, channel, random_user: Dict
    ):
        # Create a thread with multiple messages
        parent_message = await channel.send_message(
            {"text": "Parent message"}, random_user["id"]
        )
        thread_messages = []
        for i in range(3):
            msg = await channel.send_message(
                {
                    "text": f"Thread message {i}",
                    "parent_id": parent_message["message"]["id"],
                },
                random_user["id"],
            )
            thread_messages.append(msg)

        # Query threads with limit and offset
        filter_conditions = {"parent_id": parent_message["message"]["id"]}
        sort_conditions = [{"field": "created_at", "direction": -1}]

        response = await client.query_threads(
            filter=filter_conditions,
            sort=sort_conditions,
            limit=1,
            user_id=random_user["id"]
        )

        assert isinstance(response, StreamResponse)
        assert "threads" in response
        assert len(response["threads"]) == 1
        assert "next" in response
