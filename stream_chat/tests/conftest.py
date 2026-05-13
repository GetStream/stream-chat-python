import os
import sys
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


def _warn_cleanup_failure(label: str, identifier: str, exc: BaseException) -> None:
    """Surface cleanup failures in CI logs.

    Fixtures used to swallow every teardown exception with ``except Exception: pass``,
    which silently leaked test channels / users / commands into the shared CI
    app and eventually broke unrelated tests with stale-state assertions. We
    can't fail the test on cleanup error (the test itself already passed) but
    we can at least make the leak visible so the on-call dev knows where to
    look.
    """
    print(
        f"[cleanup] {label} {identifier} failed: {exc.__class__.__name__}: {exc}",
        file=sys.stderr,
    )


@pytest.fixture(scope="session", autouse=True)
def _purge_stale_test_channels():
    """Best-effort sweep of leaked test channels at session start AND end.

    Per-test fixtures tear down with synchronous ``channel.delete(hard=True)``,
    but historical runs that aborted mid-test left orphans in the shared CI
    app. This sweep targets channels tagged ``{"test": True, "language":
    "python"}`` by the ``channel`` fixture below — anything that isn't
    actively in use by another concurrent run gets hard-deleted.

    Session-scoped so it runs once per ``pytest`` invocation. autouse=True so
    even tests that don't request a channel still benefit (and the next run's
    quotas are healthy).
    """

    def sweep(client: StreamChat) -> None:
        try:
            response = client.query_channels(
                {"test": True, "language": "python"},
                sort=[{"field": "created_at", "direction": -1}],
                limit=30,
            )
        except Exception as exc:
            print(
                f"[cleanup] sweep query_channels failed: {exc.__class__.__name__}: {exc}",
                file=sys.stderr,
            )
            return
        cids = [c["channel"]["cid"] for c in response.get("channels", [])]
        if not cids:
            return
        try:
            client.delete_channels(cids, hard_delete=True)
            print(f"[cleanup] swept {len(cids)} leaked test channels", file=sys.stderr)
        except Exception as exc:
            _warn_cleanup_failure("sweep delete_channels", str(len(cids)), exc)

    base_url = os.environ.get("STREAM_HOST")
    options = {"base_url": base_url} if base_url else {}
    client = StreamChat(
        api_key=os.environ["STREAM_KEY"],
        api_secret=os.environ["STREAM_SECRET"],
        timeout=10,
        **options,
    )
    sweep(client)
    yield
    sweep(client)


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
    response = client.upsert_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    yield user
    hard_delete_users(client, [user["id"]])


@pytest.fixture(scope="function")
def server_user(client: StreamChat):
    user = {"id": str(uuid.uuid4())}
    response = client.upsert_user(user)
    assert "users" in response
    assert user["id"] in response["users"]
    yield user
    hard_delete_users(client, [user["id"]])


@pytest.fixture(scope="function")
def random_users(client: StreamChat):
    user1 = {"id": str(uuid.uuid4())}
    user2 = {"id": str(uuid.uuid4())}
    user3 = {"id": str(uuid.uuid4())}
    client.upsert_users([user1, user2, user3])
    yield [user1, user2, user3]
    hard_delete_users(client, [user1["id"], user2["id"], user3["id"]])


@pytest.fixture(scope="function")
def channel(client: StreamChat, random_user: Dict):
    channel = client.channel(
        "messaging", str(uuid.uuid4()), {"test": True, "language": "python"}
    )
    channel.create(random_user["id"])

    yield channel

    # Use the synchronous channel.delete (HTTP DELETE) instead of
    # client.delete_channels (returns task_id, races with subsequent tests
    # querying the same app). Tag failures so CI logs show the leak source.
    try:
        channel.delete(hard=True)
    except Exception as exc:
        _warn_cleanup_failure("channel", channel.cid, exc)


@pytest.fixture(scope="function")
def command(client: StreamChat):
    try:
        commands = client.list_commands()
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
                    client.delete_command(cmd["name"])
                except Exception as exc:
                    _warn_cleanup_failure("stale command", cmd["name"], exc)
    except Exception as exc:
        _warn_cleanup_failure("list_commands", "<sweep>", exc)

    response = client.create_command(
        dict(name=str(uuid.uuid4()), description="My command")
    )

    yield response["command"]

    try:
        client.delete_command(response["command"]["name"])
    except Exception as exc:
        _warn_cleanup_failure("command", response["command"]["name"], exc)


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
    try:
        client.restore_users([m["id"] for m in members])
    except Exception as exc:
        _warn_cleanup_failure("restore_users", "fellowship", exc)
    client.upsert_users(members)
    channel = client.channel(
        "team", "fellowship-of-the-ring", {"members": [m["id"] for m in members]}
    )
    channel.create("gandalf")

    yield

    try:
        channel.delete(hard=True)
    except Exception as exc:
        _warn_cleanup_failure("channel", channel.cid, exc)
    hard_delete_users(client, [m["id"] for m in members])


def hard_delete_users(client: StreamChat, user_ids: List[str]):
    try:
        client.delete_users(user_ids, "hard", conversations="hard", messages="hard")
    except Exception as exc:
        _warn_cleanup_failure("delete_users", ",".join(user_ids), exc)
