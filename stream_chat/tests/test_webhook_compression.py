"""Tests for the webhook verification + parsing helpers.

The Python SDK exposes the cross-SDK webhook contract in two layers:

* Module-level functions in :mod:`stream_chat.webhook`:

  * primitives - ``gunzip_payload``, ``decode_sqs_payload``,
    ``decode_sns_payload``, ``verify_signature``, ``parse_event``
  * composite helpers - ``verify_and_parse_webhook``,
    ``verify_and_parse_sqs``, ``verify_and_parse_sns``

* Client-instance forms on :class:`StreamChat` and
  :class:`StreamChatAsync`. They take ``api_secret`` from the client and
  delegate to the module functions.

Tests below exercise each layer with both compressed and uncompressed
payloads and confirm that bad signatures, malformed gzip / base64, and
parsed-event return values all behave as documented.
"""

import base64
import gzip
import hashlib
import hmac
import json

import pytest

from stream_chat import StreamChat, StreamChatAsync
from stream_chat.webhook import (
    GZIP_MAGIC,
    InvalidWebhookError,
    decode_sns_payload,
    decode_sqs_payload,
    gunzip_payload,
    parse_event,
    verify_and_parse_sns,
    verify_and_parse_sqs,
    verify_and_parse_webhook,
    verify_signature,
)

API_KEY = "tkey"
API_SECRET = "tsec2"
JSON_BODY = b'{"type":"message.new","message":{"text":"the quick brown fox"}}'
EVENT_DICT = {
    "type": "message.new",
    "message": {"text": "the quick brown fox"},
}


def _sign(body: bytes, secret: str = API_SECRET) -> str:
    return hmac.new(key=secret.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()


def _gzip(body: bytes) -> bytes:
    return gzip.compress(body)


def _b64(body: bytes) -> str:
    return base64.b64encode(body).decode("ascii")


@pytest.fixture
def sync_client() -> StreamChat:
    return StreamChat(api_key=API_KEY, api_secret=API_SECRET)


class TestGunzipPayload:
    def test_passthrough_plain_bytes(self):
        assert gunzip_payload(JSON_BODY) == JSON_BODY

    def test_passthrough_str_input(self):
        assert gunzip_payload(JSON_BODY.decode("utf-8")) == JSON_BODY

    def test_inflates_gzip_bytes(self):
        assert gunzip_payload(_gzip(JSON_BODY)) == JSON_BODY

    def test_returns_bytes(self):
        assert isinstance(gunzip_payload(JSON_BODY), bytes)
        assert isinstance(gunzip_payload(_gzip(JSON_BODY)), bytes)

    def test_empty_input(self):
        assert gunzip_payload(b"") == b""

    def test_short_input_below_magic_length(self):
        assert gunzip_payload(b"ab") == b"ab"

    def test_truncated_gzip_with_magic_raises(self):
        bad = GZIP_MAGIC + b"\x00\x00\x00"
        with pytest.raises(InvalidWebhookError, match=r"gzip decompression failed"):
            gunzip_payload(bad)

    def test_gunzip_payload_raises_on_corrupt_gzip(self):
        corrupt = GZIP_MAGIC + b"\x08\x00" + b"\x00" * 20
        with pytest.raises(InvalidWebhookError, match=r"gzip decompression failed"):
            gunzip_payload(corrupt)

    def test_decompresses_helloworld_fixture(self):
        gz_bytes = base64.b64decode("H4sIAGrYAWoAA8tIzcnJL88vykkBAK0g6/kKAAAA")
        assert gunzip_payload(gz_bytes) == b"helloworld"


class TestDecodeSqsPayload:
    def test_base64_only_no_compression(self):
        assert decode_sqs_payload(_b64(JSON_BODY)) == JSON_BODY

    def test_base64_plus_gzip(self):
        assert decode_sqs_payload(_b64(_gzip(JSON_BODY))) == JSON_BODY

    def test_accepts_str_input(self):
        encoded = _b64(_gzip(JSON_BODY))
        assert isinstance(encoded, str)
        assert decode_sqs_payload(encoded) == JSON_BODY

    def test_accepts_bytes_input(self):
        encoded = _b64(_gzip(JSON_BODY)).encode("ascii")
        assert decode_sqs_payload(encoded) == JSON_BODY

    def test_invalid_base64_raises(self):
        with pytest.raises(InvalidWebhookError, match=r"invalid base64 encoding"):
            decode_sqs_payload("!!!not-valid-base64!!!")

    def test_decode_sqs_payload_raises_on_invalid_base64(self):
        with pytest.raises(InvalidWebhookError, match=r"invalid base64 encoding"):
            decode_sqs_payload("not*valid*base64*data")

    def test_decodes_helloworld_base64_fixture(self):
        assert decode_sqs_payload("aGVsbG93b3JsZA==") == b"helloworld"

    def test_decodes_helloworld_base64_gzip_fixture(self):
        assert (
            decode_sqs_payload("H4sIAGrYAWoAA8tIzcnJL88vykkBAK0g6/kKAAAA")
            == b"helloworld"
        )


def _sns_envelope(inner_message: str) -> str:
    return json.dumps(
        {
            "Type": "Notification",
            "MessageId": "22b80b92-fdea-4c2c-8f9d-bdfb0c7bf324",
            "TopicArn": "arn:aws:sns:us-east-1:123456789012:stream-webhooks",
            "Message": inner_message,
            "Timestamp": "2026-05-11T10:00:00.000Z",
            "SignatureVersion": "1",
            "MessageAttributes": {
                "X-Signature": {"Type": "String", "Value": "<signature placeholder>"},
            },
        }
    )


class TestDecodeSnsPayload:
    def test_pre_extracted_message_matches_decode_sqs_payload(self):
        wrapped = _b64(_gzip(JSON_BODY))
        assert decode_sns_payload(wrapped) == decode_sqs_payload(wrapped)

    def test_pre_extracted_message_round_trip(self):
        assert decode_sns_payload(_b64(_gzip(JSON_BODY))) == JSON_BODY

    def test_unwraps_full_sns_envelope(self):
        wrapped = _b64(_gzip(JSON_BODY))
        envelope = _sns_envelope(wrapped)
        assert decode_sns_payload(envelope) == JSON_BODY

    def test_handles_envelope_with_leading_whitespace(self):
        wrapped = _b64(_gzip(JSON_BODY))
        envelope = "\n  " + _sns_envelope(wrapped)
        assert decode_sns_payload(envelope) == JSON_BODY


class TestVerifySignature:
    def test_matching(self):
        assert verify_signature(JSON_BODY, _sign(JSON_BODY), API_SECRET) is True

    def test_mismatched_returns_false(self):
        assert verify_signature(JSON_BODY, "0" * 64, API_SECRET) is False

    def test_accepts_bytes_signature(self):
        sig = _sign(JSON_BODY).encode()
        assert verify_signature(JSON_BODY, sig, API_SECRET) is True

    def test_accepts_str_body(self):
        body_str = JSON_BODY.decode("utf-8")
        assert verify_signature(body_str, _sign(JSON_BODY), API_SECRET) is True

    def test_wrong_secret_returns_false(self):
        sig = _sign(JSON_BODY, secret="other")
        assert verify_signature(JSON_BODY, sig, API_SECRET) is False

    def test_signature_must_match_uncompressed_bytes(self):
        compressed = _gzip(JSON_BODY)
        sig_over_compressed = _sign(compressed)
        assert verify_signature(JSON_BODY, sig_over_compressed, API_SECRET) is False

    def test_non_ascii_bytes_signature_returns_false(self):
        assert verify_signature(JSON_BODY, b"\xff" * 32, API_SECRET) is False

    def test_non_ascii_str_signature_returns_false(self):
        assert verify_signature(JSON_BODY, "\u2603" * 64, API_SECRET) is False

    def test_non_string_signature_returns_false(self):
        assert verify_signature(JSON_BODY, 12345, API_SECRET) is False  # type: ignore[arg-type]


class TestParseEvent:
    def test_parses_bytes(self):
        assert parse_event(JSON_BODY) == EVENT_DICT

    def test_parses_str(self):
        assert parse_event(JSON_BODY.decode("utf-8")) == EVENT_DICT

    def test_unknown_event_type_still_parses(self):
        body = b'{"type":"a.future.event","custom":42}'
        assert parse_event(body) == {"type": "a.future.event", "custom": 42}

    def test_parse_event_raises_on_invalid_json(self):
        with pytest.raises(InvalidWebhookError, match=r"invalid JSON payload"):
            parse_event(b"not json")


class TestVerifyAndParseWebhook:
    def test_plain_body(self):
        sig = _sign(JSON_BODY)
        assert verify_and_parse_webhook(JSON_BODY, sig, API_SECRET) == EVENT_DICT

    def test_gzip_body(self):
        sig = _sign(JSON_BODY)
        assert verify_and_parse_webhook(_gzip(JSON_BODY), sig, API_SECRET) == EVENT_DICT

    def test_returns_dict(self):
        sig = _sign(JSON_BODY)
        result = verify_and_parse_webhook(JSON_BODY, sig, API_SECRET)
        assert isinstance(result, dict)

    def test_signature_mismatch_raises(self):
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_webhook(JSON_BODY, "0" * 64, API_SECRET)

    def test_signature_must_be_over_uncompressed_bytes(self):
        compressed = _gzip(JSON_BODY)
        sig_over_compressed = _sign(compressed)
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_webhook(compressed, sig_over_compressed, API_SECRET)

    def test_wrong_secret_raises(self):
        sig = _sign(JSON_BODY, secret="other")
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_webhook(JSON_BODY, sig, API_SECRET)

    def test_signature_can_be_bytes(self):
        sig = _sign(JSON_BODY).encode()
        assert verify_and_parse_webhook(JSON_BODY, sig, API_SECRET) == EVENT_DICT

    def test_malformed_signature_surfaces_as_webhook_error(self):
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_webhook(JSON_BODY, b"\xff" * 32, API_SECRET)
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_webhook(JSON_BODY, "\u2603" * 64, API_SECRET)


class TestVerifyAndParseSqs:
    def test_base64_only(self):
        wrapped = _b64(JSON_BODY)
        sig = _sign(JSON_BODY)
        assert verify_and_parse_sqs(wrapped, sig, API_SECRET) == EVENT_DICT

    def test_base64_plus_gzip(self):
        wrapped = _b64(_gzip(JSON_BODY))
        sig = _sign(JSON_BODY)
        assert verify_and_parse_sqs(wrapped, sig, API_SECRET) == EVENT_DICT

    def test_signature_mismatch_raises(self):
        wrapped = _b64(_gzip(JSON_BODY))
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_sqs(wrapped, "0" * 64, API_SECRET)

    def test_signature_over_compressed_or_wrapped_bytes_rejected(self):
        wrapped = _b64(_gzip(JSON_BODY))
        sig_over_wrapped = _sign(wrapped.encode("ascii"))
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_sqs(wrapped, sig_over_wrapped, API_SECRET)

    def test_verify_and_parse_sqs_without_signature_parses(self):
        assert verify_and_parse_sqs(_b64(JSON_BODY)) == EVENT_DICT
        assert verify_and_parse_sqs(_b64(_gzip(JSON_BODY))) == EVENT_DICT
        assert verify_and_parse_sqs(_b64(_gzip(JSON_BODY)).encode()) == EVENT_DICT

    def test_static_verify_and_parse_sqs_raises_on_partial_creds(self):
        wrapped = _b64(_gzip(JSON_BODY))
        with pytest.raises(
            InvalidWebhookError,
            match=r"signature and secret must both be provided",
        ):
            verify_and_parse_sqs(wrapped, _sign(JSON_BODY))
        with pytest.raises(
            InvalidWebhookError,
            match=r"signature and secret must both be provided",
        ):
            verify_and_parse_sqs(wrapped, secret=API_SECRET)


class TestVerifyAndParseSns:
    def test_pre_extracted_message_round_trip(self):
        wrapped = _b64(_gzip(JSON_BODY))
        sig = _sign(JSON_BODY)
        assert verify_and_parse_sns(wrapped, sig, API_SECRET) == EVENT_DICT

    def test_matches_sqs_behaviour_for_pre_extracted_message(self):
        wrapped = _b64(_gzip(JSON_BODY))
        sig = _sign(JSON_BODY)
        assert verify_and_parse_sns(wrapped, sig, API_SECRET) == verify_and_parse_sqs(
            wrapped, sig, API_SECRET
        )

    def test_full_sns_envelope(self):
        wrapped = _b64(_gzip(JSON_BODY))
        envelope = _sns_envelope(wrapped)
        sig = _sign(JSON_BODY)
        assert verify_and_parse_sns(envelope, sig, API_SECRET) == EVENT_DICT

    def test_rejects_signature_over_envelope(self):
        wrapped = _b64(_gzip(JSON_BODY))
        envelope = _sns_envelope(wrapped)
        sig_over_envelope = _sign(envelope.encode("utf-8"))
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            verify_and_parse_sns(envelope, sig_over_envelope, API_SECRET)

    def test_verify_and_parse_sns_without_signature_parses(self):
        wrapped = _b64(_gzip(JSON_BODY))
        envelope = _sns_envelope(wrapped)
        assert verify_and_parse_sns(envelope) == EVENT_DICT
        assert verify_and_parse_sns(wrapped) == EVENT_DICT
        assert verify_and_parse_sns(_b64(JSON_BODY)) == EVENT_DICT


class TestSyncClientMethods:
    def test_verify_and_parse_webhook(self, sync_client: StreamChat):
        sig = _sign(JSON_BODY)
        assert sync_client.verify_and_parse_webhook(_gzip(JSON_BODY), sig) == EVENT_DICT

    def test_verify_and_parse_sqs(self, sync_client: StreamChat):
        wrapped = _b64(_gzip(JSON_BODY))
        sig = _sign(JSON_BODY)
        assert sync_client.verify_and_parse_sqs(wrapped, sig) == EVENT_DICT

    def test_verify_and_parse_sns(self, sync_client: StreamChat):
        wrapped = _b64(_gzip(JSON_BODY))
        sig = _sign(JSON_BODY)
        assert sync_client.verify_and_parse_sns(wrapped, sig) == EVENT_DICT

    def test_signature_mismatch_via_client(self, sync_client: StreamChat):
        with pytest.raises(InvalidWebhookError, match=r"signature mismatch"):
            sync_client.verify_and_parse_webhook(JSON_BODY, "0" * 64)

    def test_instance_verify_and_parse_sqs_without_signature(self):
        client = StreamChat(api_key=API_KEY, api_secret="")
        wrapped = _b64(_gzip(JSON_BODY))
        envelope = _sns_envelope(wrapped)
        assert client.verify_and_parse_sqs(wrapped) == EVENT_DICT
        assert client.verify_and_parse_sns(envelope) == EVENT_DICT


class TestSyncClientLegacyVerifyWebhook:
    """The legacy boolean helper stays unchanged for backward compatibility."""

    def test_returns_true_on_match(self, sync_client: StreamChat):
        assert sync_client.verify_webhook(JSON_BODY, _sign(JSON_BODY)) is True

    def test_returns_false_on_mismatch(self, sync_client: StreamChat):
        assert sync_client.verify_webhook(JSON_BODY, "0" * 64) is False


class TestAsyncClientMethods:
    async def test_verify_and_parse_webhook(self):
        sig = _sign(JSON_BODY)
        async with StreamChatAsync(api_key=API_KEY, api_secret=API_SECRET) as client:
            assert client.verify_and_parse_webhook(_gzip(JSON_BODY), sig) == EVENT_DICT

    async def test_verify_and_parse_sqs(self):
        wrapped = _b64(_gzip(JSON_BODY))
        sig = _sign(JSON_BODY)
        async with StreamChatAsync(api_key=API_KEY, api_secret=API_SECRET) as client:
            assert client.verify_and_parse_sqs(wrapped, sig) == EVENT_DICT

    async def test_verify_and_parse_sns(self):
        wrapped = _b64(_gzip(JSON_BODY))
        sig = _sign(JSON_BODY)
        async with StreamChatAsync(api_key=API_KEY, api_secret=API_SECRET) as client:
            assert client.verify_and_parse_sns(wrapped, sig) == EVENT_DICT
