Disabling a channel is a visibility and access toggle. The channel and all its data remain intact, but client-side read and write operations return a `403 Not Allowed` error. Server-side access is preserved for admin operations like moderation and data export.

Disabled channels still appear in query results by default. This means users see the channel in their list but receive errors when attempting to open it. To hide disabled channels from users, filter them out in your queries:


Re-enabling a channel restores full client-side access with all historical messages intact.

## Disable a Channel

```python
# disable a channel with full update
channel.update({"disabled": True})

# disable a channel with partial update
channel.update_partial(to_set={"disabled": True})

# enable a channel with full update
channel.update({"disabled": False})

# enable a channel with partial update
channel.update_partial(to_set={"disabled": False})
```

> [!NOTE]
> To prevent new messages while still allowing users to read existing messages, use [freeze the channel](/chat/docs/python/freezing_channels/) instead.
