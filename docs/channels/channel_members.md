Channel members are users who have been added to a channel and can participate in conversations. This page covers how to manage channel membership, including adding and removing members, controlling message history visibility, and managing member roles.

## Adding and Removing Members

### Adding Members

Using the `addMembers()` method adds the given users as members to a channel.

```python
channel.add_members(["thierry", "josh"])
```

> [!NOTE]
> **Note:** You can only add/remove up to 100 members at once.


Members can also be added when creating a channel:


### Removing Members

Using the `removeMembers()` method removes the given users from the channel.

```python
channel.remove_members(["tommaso"])
```

### Leaving a Channel

Users can leave a channel without moderator-level permissions. Ensure channel members have the `Leave Own Channel` permission enabled.


> [!NOTE]
> You can familiarize yourself with all permissions in the [Permissions section](/chat/docs/python/chat_permission_policies/).


## Hide History

When members join a channel, you can specify whether they have access to the channel's message history. By default, new members can see the history. Set `hide_history` to `true` to hide it for new members.

```python
channel.add_members(["thierry"], hide_history=True)
```

### Hide History Before a Specific Date

Alternatively, `hide_history_before` can be used to hide any history before a given timestamp while giving members access to later messages. The value must be a timestamp in the past in RFC 3339 format. If both parameters are defined, `hide_history_before` takes precedence over `hide_history`.

```python
from datetime import datetime, timedelta, timezone
cutoff = datetime.now(timezone.utc) - timedelta(days=7)  # Last 7 days
channel.add_members(["thierry"], hide_history_before=cutoff)
```

## System Message Parameter

You can optionally include a message object when adding or removing members that client-side SDKs will use to display a system message. This works for both adding and removing members.

```python
channel.add_members(["tommaso", "josh"], { "text": 'Tommaso joined the channel.', "user_id": 'tommaso' })
```

## Adding and Removing Moderators

Using the `addModerators()` method adds the given users as moderators (or updates their role to moderator if already members), while `demoteModerators()` removes the moderator status.

### Add Moderators

```python
channel.add_moderators(["thierry", "josh"])
```

### Remove Moderators

```python
channel.demote_moderators(["tommaso"])
```

> [!NOTE]
> These operations can only be performed server-side, and a maximum of 100 moderators can be added or removed at once.


## Member Custom Data

Custom data can be added at the channel member level. This is useful for storing member-specific information that is separate from user-level data. Ensure custom data does not exceed 5KB.

### Adding Custom Data


### Updating Member Data

Channel members can be partially updated. Only custom data and channel roles are eligible for modification. You can set or unset fields, either separately or in the same call.

```python
user_id = "amy"

# Set some fields
response = channel.update_member_partial(user_id, to_set={"hat": "blue"})

# Unset some fields
response = channel.update_member_partial(user_id, to_set=None, to_unset=["hat"])

# Set and unset in the same call
response = channel.update_member_partial(user_id, to_set={"color": "red"}, to_unset=["hat"])
```
