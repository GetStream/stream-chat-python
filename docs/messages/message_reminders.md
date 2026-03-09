Message reminders let users schedule notifications for specific messages, making it easier to follow up later. When a reminder includes a timestamp, it's like saying "remind me later about this message," and the user who set it will receive a notification at the designated time. If no timestamp is provided, the reminder functions more like a bookmark, allowing the user to save the message for later reference.

Reminders require Push V3 to be enabled - see details [here](/chat/docs/python/push_template/)

## Enabling Reminders

The Message Reminders feature must be activated at the channel level before it can be used. You have two configuration options: activate it for a single channel using configuration overrides, or enable it globally for all channels of a particular type.

```python
# Enabling it for a channel
channel.update_partial(
    config_overrides={
        "user_message_reminders": True
    }
)

# Enabling it for a channel type
client.update_channel_type("messaging", user_message_reminders=True)
```

Message reminders allow users to:

- schedule a notification after given amount of time has elapsed
- bookmark a message without specifying a deadline

## Limits

- A user cannot have more than 250 reminders scheduled
- A user can only have one reminder created per message

## Creating a Message Reminder

You can create a reminder for any message. When creating a reminder, you can specify a reminder time or save it for later without a specific time.

```python
from datetime import datetime, timedelta

# Create a reminder with a specific due date
remind_at = datetime.now() + timedelta(hours=1)
reminder = client.create_reminder('message-id', 'user-id', remind_at)

# Create a "Save for later" reminder without a specific time
reminder = client.create_reminder('message-id', 'user-id')
```

## Updating a Message Reminder

You can update an existing reminder for a message to change the reminder time.

```python
from datetime import datetime, timedelta

# Update a reminder with a new due date
remind_at = datetime.now() + timedelta(hours=2)
updated_reminder = client.update_reminder('message-id', 'user-id', remind_at)

# Convert a timed reminder to "Save for later"
updated_reminder = client.update_reminder('message-id', 'user-id', None)
```

## Deleting a Message Reminder

You can delete a reminder for a message when it's no longer needed.

```python
# Delete the reminder for the message
client.delete_reminder('message-id', 'user-id')
```

## Querying Message Reminders

The SDK allows you to fetch all reminders of the current user. You can filter, sort, and paginate through all the user's reminders.

```python
# Query reminders for a user
reminders = client.query_reminders('user-id')

# Query reminders with filters
filter_conditions = {'channel_cid': 'messaging:general'}
reminders = client.query_reminders('user-id', filter_conditions)
```

### Filtering Reminders

You can filter the reminders based on different criteria:

- `message_id` - Filter by the message that the reminder is created on.
- `remind_at` - Filter by the reminder time.
- `created_at` - Filter by the creation date.
- `channel_cid` - Filter by the channel ID.

The most common use case would be to filter by the reminder time. Like filtering overdue reminders, upcoming reminders, or reminders with no due date (saved for later).

```python
from datetime import datetime

# Filter overdue reminders
overdue_filter = {'remind_at': {'$lt': datetime.now()}}
overdue_reminders = client.query_reminders('user-id', overdue_filter)

# Filter upcoming reminders
upcoming_filter = {'remind_at': {'$gt': datetime.now()}}
upcoming_reminders = client.query_reminders('user-id', upcoming_filter)

# Filter reminders with no due date (saved for later)
saved_filter = {'remind_at': None}
saved_reminders = client.query_reminders('user-id', saved_filter)
```

### Pagination

If you have many reminders, you can paginate the results.

```python
# Load reminders with pagination
options = {'limit': 10, 'offset': 0}
reminders = client.query_reminders('user-id', {}, options)

# Load next page
next_page_options = {'limit': 10, 'offset': 10}
next_reminders = client.query_reminders('user-id', {}, next_page_options)
```

## Events

The following WebSocket events are available for message reminders:

- `reminder.created` - Triggered when a reminder is created
- `reminder.updated` - Triggered when a reminder is updated
- `reminder.deleted` - Triggered when a reminder is deleted
- `notification.reminder_due` - Triggered when a reminder's due time is reached

When a reminder's due time is reached, the server also sends a push notification to the user. Ensure push notifications are configured in your app.


## Webhooks

The same events are available as webhooks to notify your backend systems:

- `reminder.created`
- `reminder.updated`
- `reminder.deleted`
- `notification.reminder_due`

These webhook events contain the same payload structure as their WebSocket counterparts. For more information on configuring webhooks, see the [Webhooks documentation](/chat/docs/python/webhook_events/).
