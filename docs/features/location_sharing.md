Location sharing allows users to send a static position or share their real-time location with other participants in a channel. Stream Chat supports both static and live location sharing.

There are two types of location sharing:

- **Static Location**: A one-time location share that does not update over time.
- **Live Location**: A real-time location sharing that updates over time.

> [!NOTE]
> The SDK handles location message creation and updates, but location tracking must be implemented by the application using device location services.


## Enabling location sharing

The location sharing feature must be activated at the channel level before it can be used. You have two configuration options: activate it for a single channel using configuration overrides, or enable it globally for all channels of a particular type via [channel type settings](/chat/docs/python/channel_features/).

```python
# Enabling it for a channel type
client.update_channel_type(
  "messaging",
  shared_locations=True,
)
```

## Sending static location

Static location sharing allows you to send a message containing a static location.

```python
# Send a static location message
now = datetime.datetime.now(datetime.timezone.utc)
shared_location = {
    "created_by_device_id": "test_device_id",
    "latitude": 37.7749,
    "longitude": -122.4194,
    # No 'end_at' for static location
}

channel.send_message(
    {"text": "Message with static location", "shared_location": shared_location},
    user_id,
)
```

## Starting live location sharing

Live location sharing enables real-time location updates for a specified duration. The SDK manages the location message lifecycle, but your application is responsible for providing location updates.

```python
# Send a live location message (with end_at)
now = datetime.datetime.now(datetime.timezone.utc)
one_hour_later = now + datetime.timedelta(hours=1)
shared_location = {
    "created_by_device_id": "test_device_id",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "end_at": one_hour_later.isoformat(),
}

channel.send_message(
    {"text": "Message with live location", "shared_location": shared_location},
    user_id,
)
```

## Stopping live location sharing

You can stop live location sharing for a specific message using the message controller:

```python
# Update the user's live location (e.g., when device location changes)
location_data = {
    "created_by_device_id": "test_device_id",
    "latitude": new_latitude,
    "longitude": new_longitude,
}
client.update_user_location(
    user_id,
    message_id,
    location_data
)
```

## Updating live location

Your application must implement location tracking and provide updates to the SDK. The SDK handles updating all the current user's active live location messages and provides a throttling mechanism to prevent excessive API calls.

```python
# Update the user's live location (e.g., when device location changes)
location_data = {
    "created_by_device_id": "test_device_id",
    "latitude": new_latitude,
    "longitude": new_longitude,
}
client.update_user_location(
    user_id,
    message_id,
    location_data
)
```

Whenever the location is updated, the message will automatically be updated with the new location.

The SDK will also notify your application when it should start or stop location tracking as well as when the active live location messages change.


## Events

Whenever a location is created or updated, the following WebSocket events will be sent:

- `message.new`: When a new location message is created.
- `message.updated`: When a location message is updated.

> [!NOTE]
> In Dart, these events are resolved to more specific location events:
>
> - `location.shared`: When a new location message is created.
> - `location.updated`: When a location message is updated.


You can easily check if a message is a location message by checking the `message.sharedLocation` property. For example, you can use this events to render the locations in a map view.
