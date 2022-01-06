from collections.abc import MutableMapping
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, Optional

from stream_chat.types.rate_limit import RateLimitInfo


class StreamResponse(MutableMapping):
    def __init__(
        self, response_dict: Dict[str, Any], headers: Dict[str, Any], status_code: int
    ) -> None:
        self.__response_dict = response_dict
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
                limit=int(limit),
                remaining=int(remaining),
                reset=datetime.fromtimestamp(float(reset), timezone.utc),
            )

    def rate_limit(self) -> Optional[RateLimitInfo]:
        return self.__rate_limit

    def headers(self) -> Dict[str, Any]:
        return self.__headers

    def status_code(self) -> int:
        return self.__status_code

    def __setitem__(self, key: Any, value: Any) -> None:
        self.__response_dict[key] = value

    def __getitem__(self, key: Any) -> Any:
        return self.__response_dict[key]

    def __delitem__(self, key: Any) -> None:
        del self.__response_dict[key]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__response_dict)

    def __len__(self) -> int:
        return len(self.__response_dict)

    def __str__(self) -> str:
        return str(self.__response_dict)

    def __repr__(self) -> str:
        copied = self.__response_dict.copy()
        copied["headers"] = self.__headers
        copied["status_code"] = self.__status_code
        copied["rate_limit"] = (
            self.__rate_limit.as_dict() if self.__rate_limit else None
        )

        return copied.__repr__()
