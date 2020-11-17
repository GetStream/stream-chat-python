import asyncio
import os
import uuid

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
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


def pytest_configure(config):
    config.addinivalue_line("markers", "incremental: mark test incremental")


@pytest.fixture(scope="module")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
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
async def random_user(client):
    user = {"id": str(uuid.uuid4())}
    response = await client.update_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    return user


@pytest.fixture(scope="function")
async def server_user(client):
    user = {"id": str(uuid.uuid4())}
    response = await client.update_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    return user


@pytest.fixture(scope="function")
async def random_users(client):
    user1 = {"id": str(uuid.uuid4())}
    user2 = {"id": str(uuid.uuid4())}
    await client.update_users([user1, user2])
    return [user1, user2]


@pytest.fixture(scope="function")
async def channel(client, random_user):
    channel = client.channel(
        "messaging", str(uuid.uuid4()), {"test": True, "language": "python"}
    )
    await channel.create(random_user["id"])
    return channel


@pytest.fixture(scope="function")
async def command(client):
    response = await client.create_command(
        dict(name=str(uuid.uuid4()), description="My command")
    )

    yield response["command"]

    await client.delete_command(response["command"]["name"])


@pytest.fixture(scope="module")
async def fellowship_of_the_ring(client):
    members = [
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
    await client.update_users(members)
    channel = client.channel(
        "team", "fellowship-of-the-ring", {"members": [m["id"] for m in members]}
    )
    await channel.create("gandalf")
