"""Webhook verification and parsing helpers.

Stream Chat can deliver outbound events as plain JSON, gzipped JSON over
HTTP, or as base64 + gzip wrapped messages over SQS / SNS. The helpers in
this module implement the cross-SDK contract documented at
https://getstream.io/chat/docs/node/webhooks_overview/.

The composite functions (:func:`verify_and_parse_webhook`,
:func:`verify_and_parse_sqs`, :func:`verify_and_parse_sns`) are the
recommended entry points. The primitives they compose are exposed so
callers can build custom flows or run individual steps in isolation.

The Python SDK currently returns the parsed JSON as a ``dict``; typed
event classes will land in a future release.
"""

import base64
import gzip
import hashlib
import hmac
import json
import zlib
from typing import Any, Dict, Optional, Union

GZIP_MAGIC = b"\x1f\x8b"

INVALID_WEBHOOK_SIGNATURE_MISMATCH = "signature mismatch"
INVALID_WEBHOOK_INVALID_BASE64 = "invalid base64 encoding"
INVALID_WEBHOOK_GZIP_FAILED = "gzip decompression failed"
INVALID_WEBHOOK_INVALID_JSON = "invalid JSON payload"
INVALID_WEBHOOK_PARTIAL_AWS_CREDS = (
    "signature and secret must both be provided to verify the SQS/SNS payload"
)


class InvalidWebhookError(Exception):
    """Raised by every webhook primitive when verification or decoding
    fails. The cross-SDK contract is "one exception, message says why" -
    callers branch on the message text when they need mode-specific
    behaviour (signature mismatch vs invalid base64 vs corrupt gzip vs
    malformed JSON).
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"InvalidWebhookError: {self.message}"


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
    except (gzip.BadGzipFile, OSError, EOFError, zlib.error) as err:
        raise InvalidWebhookError(INVALID_WEBHOOK_GZIP_FAILED) from err


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
    except ValueError as err:
        raise InvalidWebhookError(INVALID_WEBHOOK_INVALID_BASE64) from err
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
    if isinstance(payload, (bytes, bytearray, memoryview)):
        payload = bytes(payload)
    try:
        return json.loads(payload)
    except json.JSONDecodeError as err:
        raise InvalidWebhookError(INVALID_WEBHOOK_INVALID_JSON) from err


def _verify_and_parse(
    payload_bytes: bytes,
    signature: Union[str, bytes],
    secret: str,
) -> Dict[str, Any]:
    if not verify_signature(payload_bytes, signature, secret):
        raise InvalidWebhookError(INVALID_WEBHOOK_SIGNATURE_MISMATCH)
    return parse_event(payload_bytes)


def _maybe_verify_and_parse(
    payload_bytes: bytes,
    signature: Optional[Union[str, bytes]],
    secret: Optional[str],
) -> Dict[str, Any]:
    if not signature and not secret:
        return parse_event(payload_bytes)
    if not signature or not secret:
        raise InvalidWebhookError(INVALID_WEBHOOK_PARTIAL_AWS_CREDS)
    return _verify_and_parse(payload_bytes, signature, secret)


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
    :raises InvalidWebhookError: on signature mismatch or any decode error
    """
    inflated = gunzip_payload(body)
    return _verify_and_parse(inflated, signature, secret)


def verify_and_parse_sqs(
    message_body: _BytesLike,
    signature: Optional[Union[str, bytes]] = None,
    secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Decode the SQS ``Body`` (base64, then gzip-if-magic) and return
    the parsed event.

    Stream does not attach an ``X-Signature`` to SQS deliveries: the
    transport is an IAM-authenticated AWS queue, so the queue ARN
    already proves origin. HMAC verification on top is redundant and
    is therefore optional. When ``signature`` and ``secret`` are both
    supplied the legacy verification pipeline still runs, so existing
    callers keep working unchanged.

    :param message_body: SQS message ``Body`` (string)
    :param signature: optional ``X-Signature`` message attribute value
    :param secret: optional API secret matching ``signature``
    :raises InvalidWebhookError: on signature mismatch, any decode
        error, or when only one of ``signature`` / ``secret`` is given
    """
    inflated = decode_sqs_payload(message_body)
    return _maybe_verify_and_parse(inflated, signature, secret)


def verify_and_parse_sns(
    notification_body: _BytesLike,
    signature: Optional[Union[str, bytes]] = None,
    secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Decode the SNS ``Message`` (identical to SQS handling) and return
    the parsed event.

    Stream does not attach an ``X-Signature`` to SNS deliveries: AWS
    already signs the SNS notification envelope, so verifying that the
    request really came from your topic happens at the SNS layer.
    HMAC verification on top is optional. When ``signature`` and
    ``secret`` are both supplied the legacy verification pipeline still
    runs, so existing callers keep working unchanged.

    :param notification_body: raw SNS notification body (the full
        ``{"Type":"Notification", ...}`` JSON envelope, or a
        pre-extracted ``Message`` string)
    :param signature: optional ``X-Signature`` message attribute value
    :param secret: optional API secret matching ``signature``
    :raises InvalidWebhookError: on signature mismatch, any decode
        error, or when only one of ``signature`` / ``secret`` is given
    """
    inflated = decode_sns_payload(notification_body)
    return _maybe_verify_and_parse(inflated, signature, secret)
