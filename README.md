# stream-chat-python

[![build](https://github.com/GetStream/stream-chat-python/workflows/build/badge.svg)](https://github.com/GetStream/stream-chat-python/actions) [![PyPI version](https://badge.fury.io/py/stream-chat.svg)](http://badge.fury.io/py/stream-chat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stream-chat.svg) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

---
> ### :bulb: Major update in v4.0 <
> The returned response objects are instances of [`StreamResponse`](https://github.com/GetStream/stream-chat-python/blob/master/stream_chat/types/stream_response.py) class. It inherits from `dict`, so it's fully backward compatible. Additionally, it provides other benefits such as rate limit information (`resp.rate_limit()`), response headers (`resp.headers()`) or status code (`resp.status_code()`).
---

The official Python API client for [Stream chat](https://getstream.io/chat/) a service for building chat applications.

You can sign up for a Stream account on our [Get Started](https://getstream.io/chat/get_started/) page.

You can use this library to access chat API endpoints server-side, for the client-side integrations (web and mobile) have a look at the Javascript, iOS and Android SDK libraries.

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
- Campaign API (alpha - susceptible changes and even won't be available in some regions yet)
- Rate limit in response

### Quickstart

> :bulb: The library is almost 100% typed. Feel free to enable [mypy](https://github.com/python/mypy) for our library. We will introduce more improvements in the future in this area.

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

    # we also expose some response metadata through a custom dictionary
    resp = chat.deactivate_user("bruce_lee")
    print(type(resp)) # <class 'stream_chat.types.stream_response.StreamResponse'>
    print(resp["user"]["id"]) # bruce_lee

    rate_limit = resp.rate_limit()
    print(f"{rate_limit.limit} / {rate_limit.remaining} / {rate_limit.reset}") # 60 / 59 / 2022-01-06 12:35:00+00:00

    headers = resp.headers()
    print(headers) # { 'Content-Encoding': 'gzip', 'Content-Length': '33', ... }

    status_code = resp.status_code()
    print(status_code) # 200


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

        # we also expose some response metadata through a custom dictionary
        resp = await chat.deactivate_user("bruce_lee")
        print(type(resp)) # <class 'stream_chat.types.stream_response.StreamResponse'>
        print(resp["user"]["id"]) # bruce_lee

        rate_limit = resp.rate_limit()
        print(f"{rate_limit.limit} / {rate_limit.remaining} / {rate_limit.reset}") # 60 / 59 / 2022-01-06 12:35:00+00:00

        headers = resp.headers()
        print(headers) # { 'Content-Encoding': 'gzip', 'Content-Length': '33', ... }

        status_code = resp.status_code()
        print(status_code) # 200


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

```

### Contributing

Install deps

```
pip install .[test, ci]
```

First, make sure you can run the test suite. Tests are run via py.test

```bash
export STREAM_KEY=my_api_key
export STREAM_SECRET=my_api_secret

make test
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
- Create a new dist with python `python setup.py sdist bdist_wheel`
- Upload the new distributable with twine `twine upload dist/*`

If unsure you can also test using the Pypi test servers `twine upload --repository-url https://test.pypi.org/legacy/ dist/stream-chat-VERSION-NAME.tar.gz`
