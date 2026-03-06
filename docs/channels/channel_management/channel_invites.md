Invites allow you to add users to a channel with a pending state. The invited user receives a notification and can accept or reject the invite.

Unread counts are not incremented for channels with a pending invite.

## Invite Users

```python
channel.invite_members(["thierry"])
```

## Accept an Invite

Call `acceptInvite` to accept a pending invite. You can optionally include a `message` parameter to post a system message when the user joins (e.g., "Nick joined this channel!").

```python
channel.accept_invite("thierry")
```

## Reject an Invite

Call `rejectInvite` to decline a pending invite. Client-side calls use the currently connected user. Server-side calls require a `user_id` parameter.

```python
channel.reject_invite("thierry")
```

## Query Invites by Status

Use `queryChannels` with the `invite` filter to retrieve channels based on invite status. Valid values are `pending`, `accepted`, and `rejected`.

### Query Accepted Invites

```python
client.query_channels({"invite": "accepted"})
```

### Query Rejected Invites

```python
client.query_channels({"invite": "rejected"})
```

### Query Pending Invites

```python
client.query_channels({"invite": "pending"})
```
