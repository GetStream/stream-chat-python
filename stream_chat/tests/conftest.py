import os
import uuid
from typing import Dict, List

import pytest

from stream_chat import StreamChat


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


@pytest.fixture(scope="module")
def client():
    base_url = os.environ.get("STREAM_HOST")
    options = {"base_url": base_url} if base_url else {}
    return StreamChat(
        api_key=os.environ["STREAM_KEY"],
        api_secret=os.environ["STREAM_SECRET"],
        timeout=10,
        **options,
    )


@pytest.fixture(scope="function")
def random_user(client: StreamChat):
    user = {"id": str(uuid.uuid4())}
    response = client.update_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    yield user
    hard_delete_users(client, [user["id"]])


@pytest.fixture(scope="function")
def server_user(client: StreamChat):
    user = {"id": str(uuid.uuid4())}
    response = client.update_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    yield user
    hard_delete_users(client, [user["id"]])


@pytest.fixture(scope="function")
def random_users(client: StreamChat):
    user1 = {"id": str(uuid.uuid4())}
    user2 = {"id": str(uuid.uuid4())}
    client.update_users([user1, user2])
    yield [user1, user2]
    hard_delete_users(client, [user1["id"], user2["id"]])


@pytest.fixture(scope="function")
def channel(client: StreamChat, random_user: Dict):
    channel = client.channel(
        "messaging", str(uuid.uuid4()), {"test": True, "language": "python"}
    )
    channel.create(random_user["id"])

    yield channel

    try:
        channel.delete()
    except Exception:
        pass


@pytest.fixture(scope="function")
def command(client: StreamChat):
    response = client.create_command(
        dict(name=str(uuid.uuid4()), description="My command")
    )

    yield response["command"]

    client.delete_command(response["command"]["name"])


@pytest.fixture(scope="module")
def fellowship_of_the_ring(client: StreamChat):
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
    client.update_users(members)
    channel = client.channel(
        "team", "fellowship-of-the-ring", {"members": [m["id"] for m in members]}
    )
    channel.create("gandalf")

    yield

    try:
        channel.delete()
    except Exception:
        pass
    hard_delete_users(client, [m["id"] for m in members])


def hard_delete_users(client: StreamChat, user_ids: List[str]):
    try:
        client.delete_users(user_ids, "hard", conversations="hard", messages="hard")
    except Exception:
        pass
