"""Webhook verification and parsing helpers.

Stream Chat can deliver outbound events as plain JSON, gzipped JSON over
HTTP, or as base64 + gzip wrapped messages over SQS / SNS. The helpers in
this module implement the cross-SDK contract documented at
https://getstream.io/chat/docs/node/webhooks_overview/.

The composite functions (:func:`verify_and_parse_webhook`,
:func:`parse_sqs`, :func:`parse_sns`) are the recommended entry points. The primitives they compose are exposed so
callers can build custom flows or run individual steps in isolation.

The Python SDK currently returns the parsed JSON as a ``dict``; typed
event classes will land in a future release.
"""

import base64
import gzip
import hashlib
import hmac
import json
from typing import Any, Dict, Optional, Union

from stream_chat.base.exceptions import (
    INVALID_WEBHOOK_GZIP_FAILED,
    INVALID_WEBHOOK_INVALID_BASE64,
    INVALID_WEBHOOK_INVALID_JSON,
    INVALID_WEBHOOK_SIGNATURE_MISMATCH,
    InvalidWebhookError,
)

GZIP_MAGIC = b"\x1f\x8b"

_BytesLike = Union[bytes, bytearray, memoryview, str]


def _to_bytes(body: _BytesLike) -> bytes:
    if isinstance(body, str):
        return body.encode("utf-8")
    if isinstance(body, (bytes, bytearray, memoryview)):
        return bytes(body)
    raise TypeError(f"webhook body must be bytes or str, got {type(body).__name__}")


def gunzip_payload(body: _BytesLike) -> bytes:
    """Return ``body`` unchanged unless it starts with the gzip magic
    (``1f 8b``, per RFC 1952), in which case the gzip stream is decompressed.

    Magic-byte detection (rather than relying on a header) means the same
    handler stays correct when middleware - Rails, Django, Laravel, Phoenix -
    auto-decompresses the request before your code sees it.
    """
    raw = _to_bytes(body)
    if raw[:2] != GZIP_MAGIC:
        return raw
    try:
        return gzip.decompress(raw)
    except (gzip.BadGzipFile, OSError, EOFError) as exc:
        raise InvalidWebhookError(INVALID_WEBHOOK_GZIP_FAILED) from exc


def decode_sqs_payload(body: _BytesLike) -> bytes:
    """Reverse the SQS firehose envelope.

    SQS message bodies are always base64-encoded so they remain valid
    UTF-8 over the queue. The base64-decoded bytes are gzip-decompressed
    when they begin with the gzip magic, otherwise they are returned
    as-is, which means the same call works whether or not Stream is
    compressing payloads for this app.
    """
    raw = _to_bytes(body)
    try:
        decoded = base64.b64decode(raw, validate=True)
    except ValueError as exc:
        raise InvalidWebhookError(INVALID_WEBHOOK_INVALID_BASE64) from exc
    return gunzip_payload(decoded)


def decode_sns_payload(notification_body: _BytesLike) -> bytes:
    """Reverse an SNS HTTP notification envelope.

    When ``notification_body`` is a JSON envelope
    (``{"Type":"Notification","Message":"..."}``), the inner
    ``Message`` field is extracted and run through
    :func:`decode_sqs_payload` (base64-decode, then gzip-if-magic). When
    the input is not a JSON envelope it is treated as the already-extracted
    ``Message`` string, so call sites that pre-unwrap continue to work.
    """
    raw = _to_bytes(notification_body)
    inner = _extract_sns_message(raw)
    return decode_sqs_payload(inner if inner is not None else raw)


def _extract_sns_message(notification_body: bytes) -> Optional[str]:
    trimmed = notification_body.lstrip()
    if not trimmed or trimmed[:1] != b"{":
        return None
    try:
        envelope = json.loads(trimmed)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(envelope, dict):
        return None
    message = envelope.get("Message")
    return message if isinstance(message, str) else None


def verify_signature(
    body: _BytesLike,
    signature: Union[str, bytes],
    secret: str,
) -> bool:
    """Constant-time HMAC-SHA256 verification of ``signature`` against
    the digest of ``body`` keyed by ``secret``.

    The signature is always computed over the **uncompressed** JSON
    bytes, so callers that decoded a gzipped or base64-wrapped payload
    must pass the inflated bytes here.

    A malformed ``signature`` (non-ASCII bytes, non-string types, etc.)
    is treated as a mismatch and returns ``False`` rather than raising,
    so callers can rely on the boolean contract.
    """
    raw = _to_bytes(body)
    if isinstance(signature, bytes):
        try:
            signature = signature.decode("ascii")
        except UnicodeDecodeError:
            return False
    elif not isinstance(signature, str):
        return False
    expected = hmac.new(
        key=secret.encode("utf-8"), msg=raw, digestmod=hashlib.sha256
    ).hexdigest()
    try:
        return hmac.compare_digest(expected, signature)
    except TypeError:
        return False


def parse_event(payload: _BytesLike) -> Dict[str, Any]:
    """Parse a JSON-encoded webhook event.

    Returns a ``dict`` today; typed event classes are planned for a
    future release of the Python SDK. The function name matches the
    documented primitive so callers can swap in a typed parser later
    without changing call sites.
    """
    try:
        if isinstance(payload, (bytes, bytearray, memoryview)):
            return json.loads(bytes(payload))
        return json.loads(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise InvalidWebhookError(INVALID_WEBHOOK_INVALID_JSON) from exc


def _verify_and_parse(
    payload_bytes: bytes,
    signature: Union[str, bytes],
    secret: str,
) -> Dict[str, Any]:
    if not verify_signature(payload_bytes, signature, secret):
        raise InvalidWebhookError(INVALID_WEBHOOK_SIGNATURE_MISMATCH)
    return parse_event(payload_bytes)


def verify_and_parse_webhook(
    body: _BytesLike,
    signature: Union[str, bytes],
    secret: str,
) -> Dict[str, Any]:
    """Decompress (when gzipped), verify the HMAC ``signature``, and
    return the parsed event.

    :param body: raw HTTP request body bytes Stream signed
    :param signature: ``X-Signature`` header value
    :param secret: the app's API secret
    :raises InvalidWebhookError: on signature mismatch or decode error
    """
    inflated = gunzip_payload(body)
    return _verify_and_parse(inflated, signature, secret)


def parse_sqs(message_body: _BytesLike) -> Dict[str, Any]:
    """Decode the SQS ``Body`` (base64, then gzip-if-magic) and return the
    parsed event. Stream does not HMAC-sign SQS message bodies."""

    inflated = decode_sqs_payload(message_body)
    return parse_event(inflated)


def parse_sns(message: _BytesLike) -> Dict[str, Any]:
    """Decode an SNS-delivered payload (unwraps envelope JSON when present,
    then same path as :func:`parse_sqs`). No verification step."""

    inflated = decode_sns_payload(message)
    return parse_event(inflated)
