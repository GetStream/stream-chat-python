from typing import Any, Dict, Optional

from stream_chat.types.header import StreamHeaders
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
        self.__headers = StreamHeaders(headers)
        self.__status_code = status_code
        self.__rate_limit: Optional[RateLimitInfo] = self.__headers.rate_limit()
        super(StreamResponse, self).__init__(response_dict)

    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Returns the ratelimit info of your API operation."""
        return self.__rate_limit

    def headers(self) -> Dict[str, Any]:
        """Returns the headers of the response."""
        return self.__headers.headers()

    def status_code(self) -> int:
        """Returns the HTTP status code of the response."""
        return self.__status_code

    def is_ok(self) -> bool:
        """Returns True if the status code is in the 200 range."""
        return 200 <= self.__status_code < 300
