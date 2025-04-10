from datetime import datetime, timezone
from typing import Any, Dict, Optional

from stream_chat.types.rate_limit import RateLimitInfo


class StreamHeaders(dict):
    def __init__(self, headers: Dict[str, Any]) -> None:
        super().__init__()
        self.__headers = headers
        self.__rate_limit: Optional[RateLimitInfo] = None
        limit, remaining, reset = (
            headers.get("x-ratelimit-limit"),
            headers.get("x-ratelimit-remaining"),
            headers.get("x-ratelimit-reset"),
        )
        if limit and remaining and reset:
            self.__rate_limit = RateLimitInfo(
                limit=int(self._clean_header(limit)),
                remaining=int(self._clean_header(remaining)),
                reset=datetime.fromtimestamp(
                    float(self._clean_header(reset)), timezone.utc
                ),
            )

        super(StreamHeaders, self).__init__(headers)

    def _clean_header(self, header: str) -> int:
        try:
            values = (v.strip() for v in header.split(","))
            return int(next(v for v in values if v))
        except ValueError:
            return 0

    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Returns the ratelimit info of your API operation."""
        return self.__rate_limit

    def headers(self) -> Dict[str, Any]:
        """Returns the headers of the response."""
        return self.__headers
