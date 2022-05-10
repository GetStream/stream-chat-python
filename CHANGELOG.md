# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [4.2.2](https://github.com/GetStream/stream-chat-python/compare/v4.2.1...v4.2.2) (2022-05-10)


### Features

* **verify_webhook:** bytes as signature header ([#119](https://github.com/GetStream/stream-chat-python/issues/119)) ([1658d0b](https://github.com/GetStream/stream-chat-python/commit/1658d0b2374a7edc2b9c006f4af3171e3ee85965))

### [4.2.1](https://github.com/GetStream/stream-chat-python/compare/v4.2.0...v4.2.1) (2022-04-21)

### Features

* add documentation to public methods ([#111](https://github.com/GetStream/stream-chat-python/issues/111)) ([758faa4](https://github.com/GetStream/stream-chat-python/commit/758faa475cd801c3fdecc1759b30b72629fc7786))

## [4.2.0](https://github.com/GetStream/stream-chat-python/compare/v4.1.0...v4.2.0) (2022-04-08)


### Features

* add custom event endpoint ([#103](https://github.com/GetStream/stream-chat-python/issues/103)) ([b619130](https://github.com/GetStream/stream-chat-python/commit/b61913091409f4aba2f8fa2b0f2fe97ed6da9ab0))
* add device fields ([#107](https://github.com/GetStream/stream-chat-python/issues/107)) ([3b582f5](https://github.com/GetStream/stream-chat-python/commit/3b582f51e5b9f81e618f0a6a5e81356bebc9bb3f))
* add options to export channel ([#100](https://github.com/GetStream/stream-chat-python/issues/100)) ([82f07ff](https://github.com/GetStream/stream-chat-python/commit/82f07ff5364dd1a5ee8be1b5f983cf156dcc84f3))
* add provider management ([#106](https://github.com/GetStream/stream-chat-python/issues/106)) ([9710a90](https://github.com/GetStream/stream-chat-python/commit/9710a9099d6c3d2e73a347aada07aabf4f4515d4))
* set keepalive timeout to 59s ([#101](https://github.com/GetStream/stream-chat-python/issues/101)) ([e7707ea](https://github.com/GetStream/stream-chat-python/commit/e7707ea9d500e3eb48dac38f08b2c8c33db456d3))
* swappable http client ([#102](https://github.com/GetStream/stream-chat-python/issues/102)) ([1343f43](https://github.com/GetStream/stream-chat-python/commit/1343f43caf82e415fccc6f82e8db1f42a0ca969b))
* **upser_user:** deprecated update_user in favor of upsert_user ([#109](https://github.com/GetStream/stream-chat-python/issues/109)) ([0b2a8aa](https://github.com/GetStream/stream-chat-python/commit/0b2a8aa627f386da8bcaa6a2b11e8ebe91f36f22))


### Bug Fixes

* report_id is is a uuid ([#105](https://github.com/GetStream/stream-chat-python/issues/105)) ([c4a5e24](https://github.com/GetStream/stream-chat-python/commit/c4a5e24fc658a9cebcf17ed9e3200b10f6caf94b))

## [4.1.0](https://github.com/GetStream/stream-chat-python/compare/v4.0.0...v4.1.0) (2022-01-20)


### Features

* add full feature parity ([#98](https://github.com/GetStream/stream-chat-python/issues/98)) ([02ea360](https://github.com/GetStream/stream-chat-python/commit/02ea3602df45ec6ff0a34f27cc3b2ecdb8c33faa))

## [4.0.0](https://github.com/GetStream/stream-chat-python/compare/v3.17.0...v4.0.0) (2022-01-18)


### Features

* Add ratelimit info to response object, Plus remove Python 3.6 support ([c472c0b](https://github.com/GetStream/stream-chat-python/commit/c472c0b7c43d7741a092d29920a1d31a413e9dc0))
> The returned response objects are instances of `StreamResponse` class. It inherits from `dict`, so it's fully backward compatible. Additionally, it provides other benefits such as rate limit information (`resp.rate_limit()`), response headers (`resp.headers()`) or status code (`resp.status_code()`).

## [3.17.0](https://github.com/GetStream/stream-chat-python/compare/v3.16.0...v3.17.0) (2022-01-06)

- Add options support into channel truncate
- Add options support into add members
- Add type hints
- Add internal flag report query and review endpoint support
- Improve tests and docs

## Nov 15, 2021 - 3.16.0

- Add support for assign_roles feature

## Nov 12, 2021 - 3.15.0

- Add update message partial support
- Add pin message and unpin message helpers

## Nov 1, 2021 - 3.14.0

- Add support for async endpoints
  - get_task
  - delete_users
  - delete_channels
- Add support for permissions v2
- Add convenience helpers for shadow ban
- Use json helper for unmarshal response in async
- Add support for Python 3.10

## Sep 14, 2021 - 3.13.1

- Tweak connection pool configuration for idle timeouts

## Sep 7, 2021 - 3.13.0

- Add optional message into member updates

## Aug 31, 2021 - 3.12.2

- Use post instead of get requests in query channels

## Aug 24, 2021 - 3.12.1

- Add namespace for ease of use and consistency in campaign update endpoints.

## Aug 23, 2021 - 3.12.0

- Add support for channel exports.

## Aug 20, 2021 - 3.11.2

- Set base url to edge, there is no need to set a region anymore.
- Fix file uploads from a local file.

## Aug 19, 2021 - 3.11.1

- Fix base path for listing campaigns

## Jul 5, 2021 - 3.11.0

- Update existing permission related API (/roles and /permissions endpoints)

## Jul 2, 2021 - 3.10.0

- Add support for campaign API (early alpha, can change)

## Jul 1, 2021 - 3.9.0

- Add support for search improvements (i.e. next, prev, sorting, more filters)

## May 26, 2021 - 3.8.0

- Add query_message_flags endpoint support
- Add token revoke support
- Run CI sequentially for different Python versions
- Drop codecov

## March 10, 2021 - 3.7.0

- Add get_rate_limits endpoint support

## March 10, 2021 - 3.6.0

- Add custom permission/role lifecycle endpoints

## February 26, 2021 - 3.5.0

- Support additional claims for jwt token generation

## February 22, 2021 - 3.4.0

- Add channel mute/unmute for a user

## February 22, 2021 - 3.3.0

- Add options to send message
  - for example to silence push notification on this message: `channel.send_message({"text": "hi"}, user_id, skip_push=True)`

## February 9, 2021 - 3.2.1

- Drop brotli dependency in async, causes install issues in Darwin
  - upstream needs updates

## February 8, 2021 - 3.2.0

- Add channel partial update

## January 22, 2021 - 3.1.1

- Bump pyjwt to 2.x

## January 5, 2021 - 3.1.0

- Add check SQS helper

## December 17, 2020 - 3.0.1

- Use f strings internally
- Use github actions and CI requirements to setup

## December 9, 2020 - 3.0.0

- Add async version of the client
- Make double invite accept/reject noop

## November 12, 2020 - 2.0.0

- Drop Python 3.5 and add 3.9

## November 12, 2020 - 1.7.1

- Normalize sort parameter in query endpoints

## October 20, 2020 - 1.7.0

- Added support for blocklists

## September 24, 2020 - 1.6.0

- Support for creating custom commands

## September 10, 2020 - 1.5.0

- Support for query members
- Prefer literals over constructors to simplify code

## July 23, 2020 - 1.4.0

- Support timeout while muting a user

## June 23, 2020 - 1.3.1

- Set a generic user agent for file/image get to prevent bot detection

## Apr 28, 2020 - 1.3.0

- Drop six dependency
  - `verify_webhook` is affected and expects bytes for body parameter
- Add 3.8 support

## Apr 17, 2020 - 1.2.2

- Fix version number

## Apr 17, 2020 - 1.2.1

- Allow to override client.base_url

## Mar 29, 2020 - 1.2.0

- Add support for invites

## Mar 29, 2020 - 1.1.1

- Fix client.create_token: returns a string now

## Mar 3, 2020 - 1.1.

- Add support for client.get_message

## Nov 7, 2019 - 1.0.2

- Bump crypto requirements

## Oct 21th, 2019 - 1.0.1

- Fixed app update method parameter passing

## Oct 19th, 2019 - 1.0.0

- Added support for user partial update endpoint
