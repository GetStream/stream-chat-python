from datetime import datetime, timezone

from stream_chat.types.stream_response import StreamResponse


class TestResponse:
    def test_clean_header(self):
        headers = {
            "x-ratelimit-limit": "300",
            "x-ratelimit-remaining": "299",
            "x-ratelimit-reset": "1598806800",
        }
        response = StreamResponse({}, headers, 200)
        assert response.rate_limit().limit == 300
        assert response.rate_limit().remaining == 299
        assert response.rate_limit().reset == datetime.fromtimestamp(
            1598806800, timezone.utc
        )

        headers_2 = {
            "x-ratelimit-limit": "300, 300",
            "x-ratelimit-remaining": "299, 299",
            "x-ratelimit-reset": "1598806800, 1598806800",
        }
        response = StreamResponse({}, headers_2, 200)
        assert response.rate_limit().limit == 300
        assert response.rate_limit().remaining == 299
        assert response.rate_limit().reset == datetime.fromtimestamp(
            1598806800, timezone.utc
        )

        headers_3 = {
            "x-ratelimit-limit": "garbage",
            "x-ratelimit-remaining": "garbage",
            "x-ratelimit-reset": "garbage",
        }
        response = StreamResponse({}, headers_3, 200)
        assert response.rate_limit().limit == 0
        assert response.rate_limit().remaining == 0
        assert response.rate_limit().reset == datetime.fromtimestamp(0, timezone.utc)
