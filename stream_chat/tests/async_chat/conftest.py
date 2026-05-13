import asyncio
import os
import sys
import uuid
from typing import Dict, List

import pytest

from stream_chat.async_chat import StreamChatAsync


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail(f"previous test failed ({previousfailed.name})")


def pytest_configure(config):
    config.addinivalue_line("markers", "incremental: mark test incremental")


def _warn_cleanup_failure(label: str, identifier: str, exc: BaseException) -> None:
    """See sync conftest for rationale; mirrored to keep both suites consistent."""
    print(
        f"[cleanup] {label} {identifier} failed: {exc.__class__.__name__}: {exc}",
        file=sys.stderr,
    )


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def _purge_stale_test_channels_async(event_loop):
    """Async mirror of the sync session sweep; queries channels tagged
    ``{"test": True, "language": "python"}`` and hard-deletes them at
    session start and end so leaks don't compound across runs."""

    async def sweep() -> None:
        base_url = os.environ.get("STREAM_HOST")
        options = {"base_url": base_url} if base_url else {}
        async with StreamChatAsync(
            api_key=os.environ["STREAM_KEY"],
            api_secret=os.environ["STREAM_SECRET"],
            timeout=10,
            **options,
        ) as client:
            try:
                response = await client.query_channels(
                    {"test": True, "language": "python"},
                    sort=[{"field": "created_at", "direction": -1}],
                    limit=30,
                )
            except Exception as exc:
                print(
                    f"[cleanup] sweep query_channels failed: "
                    f"{exc.__class__.__name__}: {exc}",
                    file=sys.stderr,
                )
                return
            cids = [c["channel"]["cid"] for c in response.get("channels", [])]
            if not cids:
                return
            try:
                await client.delete_channels(cids, hard_delete=True)
                print(
                    f"[cleanup] swept {len(cids)} leaked test channels",
                    file=sys.stderr,
                )
            except Exception as exc:
                _warn_cleanup_failure("sweep delete_channels", str(len(cids)), exc)

    event_loop.run_until_complete(sweep())
    yield
    event_loop.run_until_complete(sweep())


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def client():
    base_url = os.environ.get("STREAM_HOST")
    options = {"base_url": base_url} if base_url else {}
    async with StreamChatAsync(
        api_key=os.environ["STREAM_KEY"],
        api_secret=os.environ["STREAM_SECRET"],
        timeout=10,
        **options,
    ) as stream_client:
        yield stream_client


@pytest.fixture(scope="function")
async def random_user(client: StreamChatAsync):
    user = {"id": str(uuid.uuid4())}
    response = await client.upsert_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    yield user
    await hard_delete_users(client, [user["id"]])


@pytest.fixture(scope="function")
async def server_user(client: StreamChatAsync):
    user = {"id": str(uuid.uuid4())}
    response = await client.upsert_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    yield user
    await hard_delete_users(client, [user["id"]])


@pytest.fixture(scope="function")
async def random_users(client: StreamChatAsync):
    user1 = {"id": str(uuid.uuid4())}
    user2 = {"id": str(uuid.uuid4())}
    user3 = {"id": str(uuid.uuid4())}
    await client.upsert_users([user1, user2, user3])
    yield [user1, user2, user3]
    await hard_delete_users(client, [user1["id"], user2["id"], user3["id"]])


@pytest.fixture(scope="function")
async def channel(client: StreamChatAsync, random_user: Dict):
    channel = client.channel(
        "messaging", str(uuid.uuid4()), {"test": True, "language": "python"}
    )
    await channel.create(random_user["id"])
    yield channel

    # Synchronous channel.delete (HTTP DELETE), not the async-task
    # delete_channels — see sync conftest for the leak rationale.
    try:
        await channel.delete(hard=True)
    except Exception as exc:
        _warn_cleanup_failure("channel", channel.cid, exc)


@pytest.fixture(scope="function")
async def command(client: StreamChatAsync):
    try:
        commands = await client.list_commands()
        for cmd in commands.get("commands", []):
            if cmd.get("name") not in (
                "giphy",
                "imgur",
                "flag",
                "ban",
                "unban",
                "mute",
                "unmute",
            ):
                try:
                    await client.delete_command(cmd["name"])
                except Exception as exc:
                    _warn_cleanup_failure("stale command", cmd["name"], exc)
    except Exception as exc:
        _warn_cleanup_failure("list_commands", "<sweep>", exc)

    response = await client.create_command(
        dict(name=str(uuid.uuid4()), description="My command")
    )

    yield response["command"]

    try:
        await client.delete_command(response["command"]["name"])
    except Exception as exc:
        _warn_cleanup_failure("command", response["command"]["name"], exc)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def fellowship_of_the_ring(client: StreamChatAsync):
    members: List[Dict] = [
        {"id": "frodo-baggins", "name": "Frodo Baggins", "race": "Hobbit", "age": 50},
        {"id": "sam-gamgee", "name": "Samwise Gamgee", "race": "Hobbit", "age": 38},
        {"id": "gandalf", "name": "Gandalf the Grey", "race": "Istari"},
        {"id": "legolas", "name": "Legolas", "race": "Elf", "age": 500},
        {"id": "gimli", "name": "Gimli", "race": "Dwarf", "age": 139},
        {"id": "aragorn", "name": "Aragorn", "race": "Man", "age": 87},
        {"id": "boromir", "name": "Boromir", "race": "Man", "age": 40},
        {
            "id": "meriadoc-brandybuck",
            "name": "Meriadoc Brandybuck",
            "race": "Hobbit",
            "age": 36,
        },
        {"id": "peregrin-took", "name": "Peregrin Took", "race": "Hobbit", "age": 28},
    ]
    try:
        await client.restore_users([m["id"] for m in members])
    except Exception as exc:
        _warn_cleanup_failure("restore_users", "fellowship", exc)
    await client.upsert_users(members)
    channel = client.channel(
        "team", "fellowship-of-the-ring", {"members": [m["id"] for m in members]}
    )
    await channel.create("gandalf")
    yield
    try:
        await channel.delete(hard=True)
    except Exception as exc:
        _warn_cleanup_failure("channel", channel.cid, exc)
    await hard_delete_users(client, [m["id"] for m in members])


async def hard_delete_users(client: StreamChatAsync, user_ids: List[str]):
    try:
        await client.delete_users(
            user_ids, "hard", conversations="hard", messages="hard"
        )
    except Exception as exc:
        _warn_cleanup_failure("delete_users", ",".join(user_ids), exc)
