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
