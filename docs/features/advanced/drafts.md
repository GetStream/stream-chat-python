Draft messages allow users to save messages as drafts for later use. This feature is useful when users want to compose a message but aren't ready to send it yet.

## Creating a draft message

It is possible to create a draft message for a channel or a thread. Only one draft per channel/thread can exist at a time, so a newly created draft overrides the existing one.

```python
# Create/update a draft message in a channel
response = await channel.create_draft({"text": "This is a draft message"}, user_id)

# Create/update a draft message in a thread (parent message)
response = await channel.create_draft(
    {"text": "This is a draft message", "parent_id": parent_id}, user_id
)
```

## Deleting a draft message

You can delete a draft message for a channel or a thread as well.

```python
# Channel draft
await channel.delete_draft(user_id)

# Thread draft
await channel.delete_draft(user_id, parent_id=parent_id)
```

## Loading a draft message

It is also possible to load a draft message for a channel or a thread. Although, when querying channels, each channel will contain the draft message payload, in case there is one. The same for threads (parent messages). So, for the most part this function will not be needed.

```python
# Channel draft
response = await channel.get_draft(user_id)

# Thread draft
response = await channel.get_draft(user_id, parent_id=parent_id)
```

## Querying draft messages

The Stream Chat SDK provides a way to fetch all the draft messages for the current user. This can be useful to for the current user to manage all the drafts they have in one place.

```python
# Query all user drafts
response = await client.query_drafts(user_id=user_id, limit=10)

# Query drafts for certain channels and sort
response = await client.query_drafts(
    user_id,
    filter={
        "channel_cid": {"$in": ["messaging:channel-1", "messaging:channel-2"]},
    },
    sort=[{"field": "created_at", "direction": SortOrder.ASC}],
)
```

Filtering is possible on the following fields:

| Name        | Type                       | Description                    | Supported operations      | Example                                                |
| ----------- | -------------------------- | ------------------------------ | ------------------------- | ------------------------------------------------------ |
| channel_cid | string                     | the ID of the message          | $in, $eq                  | { channel_cid: { $in: [ 'channel-1', 'channel-2' ] } } |
| parent_id   | string                     | the ID of the parent message   | $in, $eq, $exists         | { parent_id: 'parent-message-id' }                     |
| created_at  | string (RFC3339 timestamp) | the time the draft was created | $eq, $gt, $lt, $gte, $lte | { created_at: { $gt: '2024-04-24T15:50:00.00Z' }       |

Sorting is possible on the `created_at` field. By default, draft messages are returned with the newest first.

### Pagination

In case the user has a lot of draft messages, you can paginate the results.

```python
# Query drafts with a limit
first_page = await client.query_drafts(user_id=user_id, options={"limit": 5})

# Query the next page
second_page = await client.query_drafts(
    user_id=user_id, options={"limit": 5, "next": first_page["next"]}
)
```

## Events

The following WebSocket events are available for draft messages:

- `draft.updated`, triggered when a draft message is updated.
- `draft.deleted`, triggered when a draft message is deleted.

You can subscribe to these events using the Stream Chat SDK.
