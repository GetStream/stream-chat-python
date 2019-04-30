import json
from json import JSONDecodeError


class StreamChannelException(Exception):
    pass


class StreamAPIException(Exception):
    def __init__(self, response):
        self.response = response
        try:
            parsed_response = json.loads(response.text)
            self.error_code = parsed_response.get("data", {}).get("code", "unknown")
            self.error_message = parsed_response.get("data", {}).get(
                "message", "unknown"
            )
        except JSONDecodeError:
            self.json_response = False

    def __repr__(self):
        if self.json_response:
            return f"StreamChat error code {self.error_code}: ${self.error_message}"
        else:
            return f"StreamChat error HTTP code: ${self.response.status_code}"
