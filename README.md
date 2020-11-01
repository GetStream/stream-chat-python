# stream-chat-python

[![Build Status](https://travis-ci.com/GetStream/stream-chat-python.svg?token=WystDPP9vxKnwsd8NwW1&branch=master)](https://travis-ci.com/GetStream/stream-chat-python) [![codecov](https://codecov.io/gh/GetStream/stream-chat-python/branch/master/graph/badge.svg?token=DM7rr9M7Kl)](https://codecov.io/gh/GetStream/stream-chat-python) [![PyPI version](https://badge.fury.io/py/stream-chat.svg)](http://badge.fury.io/py/stream-chat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stream-chat.svg)

the official Python API client for [Stream chat](https://getstream.io/chat/) a service for building chat applications.

You can sign up for a Stream account at https://getstream.io/chat/get_started/.

You can use this library to access chat API endpoints server-side, for the client-side integrations (web and mobile) have a look at the Javascript, iOS and Android SDK libraries (https://getstream.io/chat/).

### Installation

```bash
pip install stream-chat
```

### Documentation

[Official API docs](https://getstream.io/chat/docs/)

### How to build a chat app with Python tutorial

[Chat with Python, Django and React](https://github.com/GetStream/python-chat-example)

### Supported features

- Chat channels
- Messages
- Chat channel types
- User management
- Moderation API
- Push configuration
- User devices
- User search
- Channel search

### Quickstart

#### Sync

```python
from stream_chat import StreamChat


def main():
    chat = StreamChat(api_key="STREAM_KEY", api_secret="STREAM_SECRET")

    # add a user
    chat.update_user({"id": "chuck", "name": "Chuck"})

    # create a channel about kung-fu
    channel = chat.channel("messaging", "kung-fu")
    channel.create("chuck")

    # add a first message to the channel
    channel.send_message({"text": "AMA about kung-fu"}, "chuck")


if __name__ == '__main__':
    main()

```

#### Async

```python
import asyncio
from stream_chat import StreamChatAsync


async def main():
    async with StreamChatAsync(api_key="STREAM_KEY", api_secret="STREAM_SECRET") as chat:
        # add a user
        await chat.update_user({"id": "chuck", "name": "Chuck"})

        # create a channel about kung-fu
        channel = chat.channel("messaging", "kung-fu")
        await channel.create("chuck")

        # add a first message to the channel
        await channel.send_message({"text": "AMA about kung-fu"}, "chuck")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

```

### Contributing

Install pytest and pytest-asyncio

```
pip install pytest
pip install pytest-asyncio
```

First, make sure you can run the test suite. Tests are run via py.test

```bash
export STREAM_KEY=my_api_key
export STREAM_SECRET=my_api_secret

make test
```

Install black and pycodestyle

```
pip install black
pip install pycodestyle
```

Run linters

```bash
make lint
```


### Releasing a new version

In order to release new version you need to be a maintainer on Pypi.

- Update CHANGELOG
- Make sure you have twine installed (pip install twine)
- Update the version on setup.py
- Commit and push to Github
- Create a new tag for the version (eg. `v2.9.0`)
- Create a new dist with python `python setup.py sdist`
- Upload the new distributable with twine `twine upload dist/stream-chat-VERSION-NAME.tar.gz`

If unsure you can also test using the Pypi test servers `twine upload --repository-url https://test.pypi.org/legacy/ dist/stream-chat-VERSION-NAME.tar.gz`
