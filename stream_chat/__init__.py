__author__ = "Tommaso Barbugli"
__copyright__ = "Copyright 2019, Stream.io, Inc"
__license__ = "To be defined"
__version__ = "0.0.1"
__maintainer__ = "Tommaso Barbugli"
__email__ = "support@getstream.io"
__status__ = "Production"

from stream_chat import StreamChat

chat = StreamChat(api_key="STREAM_KEY", api_secret="STREAM_SECRET")

# add a user
chat.update_user({"id": "chuck", "name": "Chuck"})

channel = chat.channel("team", "kung-fu")
channel.create("chuck")

channel.send_message({"text": "AMA about kung-fu"})
