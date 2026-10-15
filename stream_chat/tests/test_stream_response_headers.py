from datetime import datetime

from stream_chat.types.stream_response import StreamResponse


class TestStreamResponseHeaders:
    def test_rate_limit_reads_headers_in_any_case(self):
        resp = StreamResponse(
            {"duration": "1ms"},
            {
                "X-Ratelimit-Limit": "1000",
                "X-Ratelimit-Remaining": "999",
                "X-Ratelimit-Reset": "1700000000",
            },
            200,
        )

        rate_limit = resp.rate_limit()
        assert rate_limit is not None
        assert rate_limit.limit == 1000
        assert rate_limit.remaining == 999
        assert type(rate_limit.reset) is datetime
        assert resp.headers()["X-Ratelimit-Limit"] == "1000"
