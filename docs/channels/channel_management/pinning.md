Channel members can pin a channel for themselves. This is a per-user setting that does not affect other members.

Pinned channels function identically to regular channels via the API, but your UI can display them separately. When a channel is pinned, the timestamp is recorded and returned as `pinned_at` in the response.

When querying channels, filter by `pinned: true` to retrieve only pinned channels, or `pinned: false` to exclude them. You can also sort by `pinned_at` to display pinned channels first.

## Pin a Channel

```python
# Get a channel
channel = client.channel("messaging", "general")

# Pin the channel for user amy
user_id = "amy"
response = channel.pin(user_id)

# Query for channels that are pinned
response = client.query_channels({"pinned": True}, user_id=user_id)

# Query for channels for specific members and show pinned first
response = client.query_channels(
    {"members": {"$in": ["amy", "ben"]}},
    {"pinned_at": -1},
    user_id=user_id
)

# Unpin the channel
response = channel.unpin(user_id)
```

## Global Pinning

Channels are pinned for a specific member. If the channel should instead be pinned for all users, this can be stored as custom data in the channel itself. The value cannot collide with existing fields, so use a value such as `globally_pinned: true`.
