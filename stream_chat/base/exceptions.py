import json
from typing import Dict


class StreamChannelException(Exception):
    pass


class StreamAPIException(Exception):
    def __init__(self, text: str, status_code: int) -> None:
        self.response_text = text
        self.status_code = status_code
        self.json_response = False

        try:
            parsed_response: Dict = json.loads(text)
            self.error_code = parsed_response.get("code", "unknown")
            self.error_message = parsed_response.get("message", "unknown")
            self.json_response = True
        except ValueError:
            pass

    def __str__(self) -> str:
        if self.json_response:
            return f'StreamChat error code {self.error_code}: {self.error_message}"'
        else:
            return f"StreamChat error HTTP code: {self.status_code}"
