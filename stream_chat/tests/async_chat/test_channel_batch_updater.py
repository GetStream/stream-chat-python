import asyncio
import uuid
from typing import Dict

import pytest

from stream_chat.async_chat import StreamChatAsync
from stream_chat.tests.async_chat.conftest import hard_delete_users
from stream_chat.types.channel_batch import ChannelsBatchOptions


class TestChannelBatchUpdater:
    @pytest.mark.asyncio
    async def test_update_channels_batch_none_options(self, client: StreamChatAsync):
        """Test that update_channels_batch raises error when options is None"""
        with pytest.raises(ValueError, match="options must not be None"):
            await client.update_channels_batch(None)

    @pytest.mark.asyncio
    async def test_update_channels_batch_valid_options(
        self, client: StreamChatAsync, random_user: Dict
    ):
        """Test batch update channels with valid options"""
        # Create two channels
        ch1 = client.channel("messaging", str(uuid.uuid4()))
        await ch1.create(random_user["id"])

        ch2 = client.channel("messaging", str(uuid.uuid4()))
        await ch2.create(random_user["id"])

        try:
            # Create a user to add
            user_to_add = {"id": str(uuid.uuid4())}
            await client.upsert_user(user_to_add)

            # Perform batch update
            options: ChannelsBatchOptions = {
                "operation": "addMembers",
                "filter": {"cids": {"$in": [ch1.cid, ch2.cid]}},
                "members": [{"user_id": user_to_add["id"]}],
            }

            response = await client.update_channels_batch(options)
            assert "task_id" in response
            assert len(response["task_id"]) > 0

            # Cleanup
            await hard_delete_users(client, [user_to_add["id"]])
        finally:
            try:
                await client.delete_channels([ch1.cid, ch2.cid], hard_delete=True)
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_channel_batch_updater_add_members(
        self, client: StreamChatAsync, random_user: Dict
    ):
        """Test ChannelBatchUpdater.add_members"""
        # Create two channels
        ch1 = client.channel("messaging", str(uuid.uuid4()))
        await ch1.create(random_user["id"])

        ch2 = client.channel("messaging", str(uuid.uuid4()))
        await ch2.create(random_user["id"])

        try:
            # Create users to add
            users_to_add = [{"id": str(uuid.uuid4())}, {"id": str(uuid.uuid4())}]
            await client.upsert_users(users_to_add)

            updater = client.channel_batch_updater()

            members = [{"user_id": user["id"]} for user in users_to_add]

            response = await updater.add_members(
                {"cids": {"$in": [ch1.cid, ch2.cid]}}, members
            )
            assert "task_id" in response
            task_id = response["task_id"]

            # Wait for task to complete
            await asyncio.sleep(2)

            # Poll for task completion
            for _ in range(120):
                task = await client.get_task(task_id)
                if task["status"] in ["waiting", "pending", "running"]:
                    await asyncio.sleep(1)
                    continue

                if task["status"] == "completed":
                    # Wait a bit and verify members were added to both channels
                    for _ in range(120):
                        await asyncio.sleep(1)
                        ch1_members = await ch1.query_members({})
                        ch2_members = await ch2.query_members({})

                        ch1_member_ids = [m["user_id"] for m in ch1_members]
                        ch2_member_ids = [m["user_id"] for m in ch2_members]
                        all_found_ch1 = all(
                            user_id in ch1_member_ids
                            for user_id in [u["id"] for u in users_to_add]
                        )
                        all_found_ch2 = all(
                            user_id in ch2_member_ids
                            for user_id in [u["id"] for u in users_to_add]
                        )
                        if all_found_ch1 and all_found_ch2:
                            return

                    pytest.fail("changes not visible after 2 minutes")

                if task["status"] == "failed":
                    if len(task.get("result", {})) == 0:
                        await asyncio.sleep(2)
                        continue
                    desc = task.get("result", {}).get("description", "")
                    if "rate limit" in desc.lower():
                        await asyncio.sleep(2)
                        continue
                    pytest.fail(f"task failed with result: {task.get('result')}")

                await asyncio.sleep(1)

            pytest.fail("task did not complete in 2 minutes")

        finally:
            try:
                await hard_delete_users(client, [u["id"] for u in users_to_add])
                await client.delete_channels([ch1.cid, ch2.cid], hard_delete=True)
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_channel_batch_updater_remove_members(
        self, client: StreamChatAsync, random_user: Dict
    ):
        """Test ChannelBatchUpdater.remove_members"""
        # Create users
        members_id = [str(uuid.uuid4()), str(uuid.uuid4())]
        users = [{"id": uid} for uid in members_id]
        await client.upsert_users(users)

        # Create channels with members
        ch1 = client.channel("messaging", str(uuid.uuid4()))
        await ch1.create(random_user["id"])
        for member_id in members_id:
            await ch1.add_members([member_id])

        ch2 = client.channel("messaging", str(uuid.uuid4()))
        await ch2.create(random_user["id"])
        for member_id in members_id:
            await ch2.add_members([member_id])

        try:
            # Verify members are present
            ch1_members = await ch1.query_members({})
            ch2_members = await ch2.query_members({})
            assert len(ch1_members) >= 2
            assert len(ch2_members) >= 2

            ch1_member_ids = [m["user_id"] for m in ch1_members]
            ch2_member_ids = [m["user_id"] for m in ch2_members]
            assert all(mid in ch1_member_ids for mid in members_id)
            assert all(mid in ch2_member_ids for mid in members_id)

            # Remove a member
            updater = client.channel_batch_updater()
            member_to_remove = members_id[0]

            response = await updater.remove_members(
                {"cids": {"$in": [ch1.cid, ch2.cid]}},
                [{"user_id": member_to_remove}],
            )
            assert "task_id" in response
            task_id = response["task_id"]

            # Wait for task to complete
            await asyncio.sleep(2)

            # Poll for task completion
            for _ in range(120):
                task = await client.get_task(task_id)
                if task["status"] in ["waiting", "pending", "running"]:
                    await asyncio.sleep(1)
                    continue

                if task["status"] == "completed":
                    # Wait a bit and verify member was removed
                    for _ in range(120):
                        await asyncio.sleep(1)
                        ch1_members = await ch1.query_members({})

                        ch1_member_ids = [m["user_id"] for m in ch1_members]
                        if member_to_remove not in ch1_member_ids:
                            return

                    pytest.fail(
                        f"changes not visible after 2 minutes. Channel 1 still has members: {ch1_member_ids}"
                    )

                if task["status"] == "failed":
                    if len(task.get("result", {})) == 0:
                        await asyncio.sleep(2)
                        continue
                    desc = task.get("result", {}).get("description", "")
                    if "rate limit" in desc.lower():
                        await asyncio.sleep(2)
                        continue
                    pytest.fail(f"task failed with result: {task.get('result')}")

                await asyncio.sleep(1)

            pytest.fail("task did not complete in 2 minutes")

        finally:
            try:
                await hard_delete_users(client, members_id)
                await client.delete_channels([ch1.cid, ch2.cid], hard_delete=True)
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_channel_batch_updater_archive(
        self, client: StreamChatAsync, random_user: Dict
    ):
        """Test ChannelBatchUpdater.archive"""
        # Create users
        members_id = [str(uuid.uuid4()), str(uuid.uuid4())]
        users = [{"id": uid} for uid in members_id]
        await client.upsert_users(users)

        # Create channels with members
        ch1 = client.channel("messaging", str(uuid.uuid4()))
        await ch1.create(random_user["id"])
        for member_id in members_id:
            await ch1.add_members([member_id])

        ch2 = client.channel("messaging", str(uuid.uuid4()))
        await ch2.create(random_user["id"])
        for member_id in members_id:
            await ch2.add_members([member_id])

        try:
            updater = client.channel_batch_updater()

            response = await updater.archive(
                {"cids": {"$in": [ch1.cid, ch2.cid]}},
                [{"user_id": members_id[0]}],
            )
            assert "task_id" in response
            task_id = response["task_id"]

            # Wait for task to complete
            await asyncio.sleep(2)

            # Poll for task completion
            for _ in range(120):
                task = await client.get_task(task_id)
                if task["status"] in ["waiting", "pending", "running"]:
                    await asyncio.sleep(1)
                    continue

                if task["status"] == "completed":
                    # Wait a bit and verify channel was archived
                    for _ in range(120):
                        await asyncio.sleep(1)
                        ch1_state = await ch1.query()

                        # Check archived_at in channel state for the user
                        if "channel" in ch1_state and "members" in ch1_state["channel"]:
                            for m in ch1_state["channel"]["members"]:
                                if m["user_id"] == members_id[0]:
                                    if m.get("archived_at") is not None:
                                        return
                                    break
                        # Also check top-level members if present
                        if "members" in ch1_state:
                            for m in ch1_state["members"]:
                                if m["user_id"] == members_id[0]:
                                    if m.get("archived_at") is not None:
                                        return
                                    break

                    pytest.fail("changes not visible after 2 minutes")

                if task["status"] == "failed":
                    if len(task.get("result", {})) == 0:
                        await asyncio.sleep(2)
                        continue
                    desc = task.get("result", {}).get("description", "")
                    if "rate limit" in desc.lower():
                        await asyncio.sleep(2)
                        continue
                    pytest.fail(f"task failed with result: {task.get('result')}")

                await asyncio.sleep(1)

            pytest.fail("task did not complete in 2 minutes")

        finally:
            try:
                await hard_delete_users(client, members_id)
                await client.delete_channels([ch1.cid, ch2.cid], hard_delete=True)
            except Exception:
                pass
