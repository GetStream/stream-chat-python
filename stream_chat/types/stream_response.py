from datetime import datetime, timezone
from typing import Any, Dict, Optional

from stream_chat.types.rate_limit import RateLimitInfo


class StreamResponse(dict):
    """
    A custom dictionary where you can access the response data the same way
    as a normal dictionary. Additionally, we expose some methods to access other metadata.

    ::

        resp = client.get_app_settings()
        print(resp["app"]["webhook_url"])
        # "https://mycompany.com/webhook"
        rate_limit = resp.rate_limit()
        print(rate_limit.remaining)
        # 99
        headers = resp.headers()
        print(headers["content-type"])
        # "application/json;charset=utf-8"
        status_code = resp.status_code()
        print(status_code)
        # 200
    """

    def __init__(
        self, response_dict: Dict[str, Any], headers: Dict[str, Any], status_code: int
    ) -> None:
        self.__headers = headers
        self.__status_code = status_code
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

        super(StreamResponse, self).__init__(response_dict)

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

    def status_code(self) -> int:
        """Returns the HTTP status code of the response."""
        return self.__status_code
