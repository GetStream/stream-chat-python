# Official Python SDK for [Stream Chat](https://getstream.io/chat/)

[![build](https://github.com/GetStream/stream-chat-python/workflows/build/badge.svg)](https://github.com/GetStream/stream-chat-python/actions) [![PyPI version](https://badge.fury.io/py/stream-chat.svg)](http://badge.fury.io/py/stream-chat) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stream-chat.svg) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

<p align="center">
    <img src="./assets/logo.svg" width="50%" height="50%">
</p>
<p align="center">
    Official Python API client for Stream Chat, a service for building chat applications.
    <br />
    <a href="https://getstream.io/chat/docs/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/GetStream/python-chat-example">Code Samples</a>
    ·
    <a href="https://github.com/GetStream/stream-chat-python/issues">Report Bug</a>
    ·
    <a href="https://github.com/GetStream/stream-chat-python/issues">Request Feature</a>
</p>

---
> ### :bulb: Major update in v4.0 <
> The returned response objects are instances of [`StreamResponse`](https://github.com/GetStream/stream-chat-python/blob/master/stream_chat/types/stream_response.py) class. It inherits from `dict`, so it's fully backward compatible. Additionally, it provides other benefits such as rate limit information (`resp.rate_limit()`), response headers (`resp.headers()`) or status code (`resp.status_code()`).
---

## 📝 About Stream

You can sign up for a Stream account at our [Get Started](https://getstream.io/chat/get_started/) page.

You can use this library to access chat API endpoints server-side.

For the client-side integrations (web and mobile) have a look at the JavaScript, iOS and Android SDK libraries ([docs](https://getstream.io/chat/)).

## ⚙️ Installation

```shell
$ pip install stream-chat
```

## ✨ Getting started

> :bulb: The library is almost 100% typed. Feel free to enable [mypy](https://github.com/python/mypy) for our library. We will introduce more improvements in the future in this area.

```python
from stream_chat import StreamChat

chat = StreamChat(api_key="STREAM_KEY", api_secret="STREAM_SECRET")

# add a user
chat.upsert_user({"id": "chuck", "name": "Chuck"})

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
print(f"{rate_limit.limit} / {rate_limit.remaining} / {rate_limit.reset}") # 60 / 59 /2022-01-06 12:35:00+00:00

headers = resp.headers()
print(headers) # { 'Content-Encoding': 'gzip', 'Content-Length': '33', ... }

status_code = resp.status_code()
print(status_code) # 200

```

### Async

```python
import asyncio
from stream_chat import StreamChatAsync


async def main():
    async with StreamChatAsync(api_key="STREAM_KEY", api_secret="STREAM_SECRET") as chat:
        # add a user
        await chat.upsert_user({"id": "chuck", "name": "Chuck"})

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

## ✍️ Contributing

We welcome code changes that improve this library or fix a problem, please make sure to follow all best practices and add tests if applicable before submitting a Pull Request on Github. We are very happy to merge your code in the official repository. Make sure to sign our [Contributor License Agreement (CLA)](https://docs.google.com/forms/d/e/1FAIpQLScFKsKkAJI7mhCr7K9rEIOpqIDThrWxuvxnwUq2XkHyG154vQ/viewform) first. See our [license file](./LICENSE) for more details.

Head over to [CONTRIBUTING.md](./CONTRIBUTING.md) for some development tips.

## 🧑‍💻 We are hiring!

We've recently closed a [$38 million Series B funding round](https://techcrunch.com/2021/03/04/stream-raises-38m-as-its-chat-and-activity-feed-apis-power-communications-for-1b-users/) and we keep actively growing.
Our APIs are used by more than a billion end-users, and you'll have a chance to make a huge impact on the product within a team of the strongest engineers all over the world.

Check out our current openings and apply via [Stream's website](https://getstream.io/team/#jobs).
