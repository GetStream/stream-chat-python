Scheduled messages let a user write a message now and have it sent to a channel later. Until it is sent, a scheduled message is visible only to the user who scheduled it and to server-side callers. Server-side, you can schedule, update, cancel, send and list the scheduled messages of any user.

Scheduled messages must be enabled for your app. Requests return an error with the `scheduled_messages_disabled` reason otherwise.

## Limits

- The send time must be at least 1 minute and at most the app's maximum lead time (120 days by default) from now
- A user can have at most 100 scheduled messages, and at most 10 in one channel (app defaults)
- Slash commands cannot be scheduled

## Scheduling a Message

Pass `scheduled_at` to `send_message`. It accepts a `datetime` (a naive one is taken to be in UTC) or an ISO 8601 string. The message is stored instead of sent, and the response carries the scheduled message.

```python
from datetime import datetime, timedelta, timezone

response = channel.send_message(
    {"text": "See you tomorrow"},
    "user-id",
    scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
)

scheduled = response["scheduled_message"]
print(scheduled["id"], scheduled["status"], scheduled["scheduled_at"])
```

`response["message"]` holds the content as it will be sent; it is not in the channel yet, and its ID is the scheduled message ID. The ID of the sent message is only known when it is sent (see the `scheduled_message.sent` event below).

## Updating a Scheduled Message

Change the message, the send time, or both. A new message replaces the scheduled one as a whole.

```python
client.update_scheduled_message(
    scheduled["id"],
    message={"text": "See you the day after"},
    scheduled_at=datetime.now(timezone.utc) + timedelta(days=2),
)

# Only move the send time
client.update_scheduled_message(
    scheduled["id"], scheduled_at=datetime.now(timezone.utc) + timedelta(days=2)
)
```

## Sending a Scheduled Message Now

```python
client.send_scheduled_message_now(scheduled["id"])
```

## Deleting a Scheduled Message

Cancels a scheduled message so it is never sent, or removes one that failed to send.

```python
client.delete_scheduled_message(scheduled["id"])
```

Update, send now and delete return an error while the message is being sent. A message that failed to send can only be deleted.

## Querying Scheduled Messages

Lists the pending (`scheduled`, `sending`) and `failed` messages of one user across channels: pending ones first, then failed ones, each by send time.

```python
response = client.query_scheduled_messages(
    "user-id",
    filter={"cid": "messaging:general", "status": ["failed"]},
    options={"limit": 20},
)

# Next page
if response.get("next"):
    response = client.query_scheduled_messages(
        "user-id", options={"next": response["next"]}
    )
```

## Events

| Event | Webhook | Description |
| --- | --- | --- |
| `scheduled_message.created` | No | A message was scheduled |
| `scheduled_message.updated` | No | A scheduled message was updated or sent now |
| `scheduled_message.deleted` | No | A scheduled message was canceled |
| `scheduled_message.sent` | Yes | A scheduled message was sent. `message_id` holds the ID of the sent message |
| `scheduled_message.failed` | Yes | A scheduled message failed to send. `scheduled_message.failure_reason` says why |
