import json
from typing import Any, Dict, Optional

from stream_chat.types.header import StreamHeaders
from stream_chat.types.rate_limit import RateLimitInfo


class StreamChannelException(Exception):
    pass


class StreamAPIException(Exception):
    def __init__(
        self, text: str, status_code: int, headers: Dict[str, Any] = {}
    ) -> None:
        self.response_text = text
        self.status_code = status_code
        self.json_response = False
        self.headers = StreamHeaders(headers)
        self.__rate_limit: Optional[RateLimitInfo] = self.headers.rate_limit()

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

    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Returns the ratelimit info of your API operation."""
        return self.__rate_limit
