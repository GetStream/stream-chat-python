import base64
import gzip
import hashlib
import hmac

import pytest

from stream_chat import StreamChat, StreamChatAsync
from stream_chat.base.exceptions import WebhookSignatureError
from stream_chat.webhook import (
    decompress_webhook_body,
    verify_and_decode_webhook,
)

API_KEY = "tkey"
API_SECRET = "tsec2"
JSON_BODY = b'{"type":"message.new","message":{"text":"the quick brown fox"}}'


def _sign(body: bytes, secret: str = API_SECRET) -> str:
    return hmac.new(key=secret.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()


def _gzip(body: bytes) -> bytes:
    return gzip.compress(body)


def _b64(body: bytes) -> bytes:
    return base64.b64encode(body)


@pytest.fixture
def sync_client() -> StreamChat:
    return StreamChat(api_key=API_KEY, api_secret=API_SECRET)


class TestVerifyWebhookBackwardCompat:
    def test_verify_webhook_matches_signature(self, sync_client: StreamChat):
        signature = _sign(JSON_BODY)
        assert sync_client.verify_webhook(JSON_BODY, signature) is True

    def test_verify_webhook_rejects_bad_signature(self, sync_client: StreamChat):
        assert sync_client.verify_webhook(JSON_BODY, "0" * 64) is False

    def test_verify_webhook_accepts_bytes_signature(self, sync_client: StreamChat):
        signature = _sign(JSON_BODY).encode()
        assert sync_client.verify_webhook(JSON_BODY, signature) is True


class TestDecompressWebhookBody:
    def test_passthrough_when_no_encodings(self):
        assert decompress_webhook_body(JSON_BODY) == JSON_BODY

    def test_passthrough_when_encodings_are_empty_strings(self):
        assert (
            decompress_webhook_body(JSON_BODY, content_encoding="", payload_encoding="")
            == JSON_BODY
        )

    def test_passthrough_when_encodings_are_none(self):
        assert (
            decompress_webhook_body(
                JSON_BODY, content_encoding=None, payload_encoding=None
            )
            == JSON_BODY
        )

    def test_gzip_round_trip_bytes(self):
        compressed = _gzip(JSON_BODY)
        assert decompress_webhook_body(compressed, content_encoding="gzip") == JSON_BODY

    def test_gzip_round_trip_str_input(self):
        compressed = _gzip(JSON_BODY)
        wrapped = compressed.decode("latin-1")
        assert (
            decompress_webhook_body(wrapped.encode("latin-1"), content_encoding="gzip")
            == JSON_BODY
        )

    def test_base64_round_trip_no_compression(self):
        wrapped = _b64(JSON_BODY)
        assert decompress_webhook_body(wrapped, payload_encoding="base64") == JSON_BODY

    def test_base64_str_input(self):
        wrapped_str = _b64(JSON_BODY).decode("ascii")
        assert (
            decompress_webhook_body(wrapped_str, payload_encoding="base64") == JSON_BODY
        )

    def test_base64_plus_gzip_round_trip(self):
        wrapped = _b64(_gzip(JSON_BODY))
        assert (
            decompress_webhook_body(
                wrapped, content_encoding="gzip", payload_encoding="base64"
            )
            == JSON_BODY
        )

    @pytest.mark.parametrize(
        "content_encoding",
        ["GZIP", "Gzip", " gzip ", "gZiP"],
    )
    def test_content_encoding_is_case_insensitive(self, content_encoding: str):
        compressed = _gzip(JSON_BODY)
        assert (
            decompress_webhook_body(compressed, content_encoding=content_encoding)
            == JSON_BODY
        )

    @pytest.mark.parametrize(
        "payload_encoding",
        ["BASE64", "Base64", " base64 ", "B64", "b64", " b64 "],
    )
    def test_payload_encoding_aliases_and_case(self, payload_encoding: str):
        wrapped = _b64(JSON_BODY)
        assert (
            decompress_webhook_body(wrapped, payload_encoding=payload_encoding)
            == JSON_BODY
        )

    @pytest.mark.parametrize(
        "content_encoding", ["br", "brotli", "zstd", "deflate", "compress", "lz4"]
    )
    def test_unsupported_content_encoding(self, content_encoding: str):
        with pytest.raises(ValueError) as exc_info:
            decompress_webhook_body(JSON_BODY, content_encoding=content_encoding)
        message = str(exc_info.value).lower()
        assert "unsupported" in message
        assert "gzip" in message

    @pytest.mark.parametrize("payload_encoding", ["hex", "url", "binary"])
    def test_unsupported_payload_encoding(self, payload_encoding: str):
        with pytest.raises(ValueError) as exc_info:
            decompress_webhook_body(JSON_BODY, payload_encoding=payload_encoding)
        message = str(exc_info.value).lower()
        assert "unsupported" in message
        assert "payload_encoding" in message

    def test_invalid_gzip_bytes_raises(self):
        with pytest.raises(WebhookSignatureError) as exc_info:
            decompress_webhook_body(b"this is not gzip data", content_encoding="gzip")
        assert "decompress" in str(exc_info.value).lower()

    def test_invalid_base64_input_raises(self):
        with pytest.raises(WebhookSignatureError) as exc_info:
            decompress_webhook_body(
                b"!!!not-valid-base64!!!", payload_encoding="base64"
            )
        assert "payload_encoding" in str(exc_info.value).lower()

    def test_returns_bytes_type(self):
        result = decompress_webhook_body(JSON_BODY)
        assert isinstance(result, bytes)

    def test_unsupported_message_includes_value(self):
        with pytest.raises(ValueError) as exc_info:
            decompress_webhook_body(JSON_BODY, content_encoding="brotli")
        assert "brotli" in str(exc_info.value)


class TestVerifyAndDecodeWebhookHelper:
    def test_happy_path_plain(self):
        signature = _sign(JSON_BODY)
        assert (
            verify_and_decode_webhook(JSON_BODY, signature, api_secret=API_SECRET)
            == JSON_BODY
        )

    def test_happy_path_gzip(self):
        compressed = _gzip(JSON_BODY)
        signature = _sign(JSON_BODY)
        assert (
            verify_and_decode_webhook(
                compressed,
                signature,
                api_secret=API_SECRET,
                content_encoding="gzip",
            )
            == JSON_BODY
        )

    def test_happy_path_base64_plus_gzip(self):
        wrapped = _b64(_gzip(JSON_BODY))
        signature = _sign(JSON_BODY)
        assert (
            verify_and_decode_webhook(
                wrapped,
                signature,
                api_secret=API_SECRET,
                content_encoding="gzip",
                payload_encoding="base64",
            )
            == JSON_BODY
        )

    def test_signature_mismatch_raises(self):
        with pytest.raises(WebhookSignatureError) as exc_info:
            verify_and_decode_webhook(JSON_BODY, "0" * 64, api_secret=API_SECRET)
        assert "invalid webhook signature" in str(exc_info.value).lower()

    def test_signature_over_compressed_bytes_raises(self):
        compressed = _gzip(JSON_BODY)
        signature_over_compressed = _sign(compressed)
        with pytest.raises(WebhookSignatureError):
            verify_and_decode_webhook(
                compressed,
                signature_over_compressed,
                api_secret=API_SECRET,
                content_encoding="gzip",
            )

    def test_signature_over_wrapped_bytes_raises(self):
        wrapped = _b64(_gzip(JSON_BODY))
        signature_over_wrapped = _sign(wrapped)
        with pytest.raises(WebhookSignatureError):
            verify_and_decode_webhook(
                wrapped,
                signature_over_wrapped,
                api_secret=API_SECRET,
                content_encoding="gzip",
                payload_encoding="base64",
            )

    def test_bad_secret_raises(self):
        signature = _sign(JSON_BODY, secret="other")
        with pytest.raises(WebhookSignatureError):
            verify_and_decode_webhook(JSON_BODY, signature, api_secret=API_SECRET)

    def test_signature_can_be_bytes(self):
        signature = _sign(JSON_BODY).encode()
        assert (
            verify_and_decode_webhook(JSON_BODY, signature, api_secret=API_SECRET)
            == JSON_BODY
        )


class TestSyncClientMethods:
    def test_decompress_via_client(self, sync_client: StreamChat):
        wrapped = _b64(_gzip(JSON_BODY))
        assert (
            sync_client.decompress_webhook_body(
                wrapped, content_encoding="gzip", payload_encoding="base64"
            )
            == JSON_BODY
        )

    def test_verify_and_decode_via_client(self, sync_client: StreamChat):
        signature = _sign(JSON_BODY)
        compressed = _gzip(JSON_BODY)
        assert (
            sync_client.verify_and_decode_webhook(
                compressed, signature, content_encoding="gzip"
            )
            == JSON_BODY
        )

    def test_verify_and_decode_via_client_signature_mismatch(
        self, sync_client: StreamChat
    ):
        with pytest.raises(WebhookSignatureError):
            sync_client.verify_and_decode_webhook(JSON_BODY, "0" * 64)


class TestAsyncClientMethods:
    async def test_async_verify_and_decode_happy_path(self):
        signature = _sign(JSON_BODY)
        compressed = _gzip(JSON_BODY)
        async with StreamChatAsync(api_key=API_KEY, api_secret=API_SECRET) as client:
            assert (
                client.verify_and_decode_webhook(
                    compressed, signature, content_encoding="gzip"
                )
                == JSON_BODY
            )
