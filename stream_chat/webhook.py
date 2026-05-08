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
import binascii
import gzip
import hashlib
import hmac
import json
from typing import Any, Dict, Union

from stream_chat.base.exceptions import WebhookSignatureError

GZIP_MAGIC = b"\x1f\x8b\x08"

_BytesLike = Union[bytes, bytearray, memoryview, str]


def _to_bytes(body: _BytesLike) -> bytes:
    if isinstance(body, str):
        return body.encode("utf-8")
    if isinstance(body, (bytes, bytearray, memoryview)):
        return bytes(body)
    raise TypeError(f"webhook body must be bytes or str, got {type(body).__name__}")


def ungzip_payload(body: _BytesLike) -> bytes:
    """Return ``body`` unchanged unless it starts with the gzip magic
    (``1f 8b 08``), in which case the gzip stream is decompressed.

    Magic-byte detection (rather than relying on a header) means the same
    handler stays correct when middleware - Rails, Django, Laravel, Phoenix -
    auto-decompresses the request before your code sees it.
    """
    raw = _to_bytes(body)
    if raw[:3] != GZIP_MAGIC:
        return raw
    try:
        return gzip.decompress(raw)
    except (gzip.BadGzipFile, OSError, EOFError) as exc:
        raise WebhookSignatureError(f"failed to decompress gzip payload: {exc}")


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
    except (binascii.Error, ValueError) as exc:
        raise WebhookSignatureError(f"failed to base64-decode payload: {exc}")
    return ungzip_payload(decoded)


def decode_sns_payload(message: _BytesLike) -> bytes:
    """Reverse the SNS firehose envelope. Byte-for-byte identical to
    :func:`decode_sqs_payload`; exposed under both names so call sites
    read intent."""
    return decode_sqs_payload(message)


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
    """
    raw = _to_bytes(body)
    if isinstance(signature, bytes):
        signature = signature.decode("ascii")
    expected = hmac.new(
        key=secret.encode("utf-8"), msg=raw, digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_event(payload: _BytesLike) -> Dict[str, Any]:
    """Parse a JSON-encoded webhook event.

    Returns a ``dict`` today; typed event classes are planned for a
    future release of the Python SDK. The function name matches the
    documented primitive so callers can swap in a typed parser later
    without changing call sites.
    """
    if isinstance(payload, (bytes, bytearray, memoryview)):
        return json.loads(bytes(payload))
    return json.loads(payload)


def _verify_and_parse(
    payload_bytes: bytes,
    signature: Union[str, bytes],
    secret: str,
) -> Dict[str, Any]:
    if not verify_signature(payload_bytes, signature, secret):
        raise WebhookSignatureError("invalid webhook signature")
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
    :raises WebhookSignatureError: on signature mismatch or decode error
    """
    inflated = ungzip_payload(body)
    return _verify_and_parse(inflated, signature, secret)


def verify_and_parse_sqs(
    message_body: _BytesLike,
    signature: Union[str, bytes],
    secret: str,
) -> Dict[str, Any]:
    """Decode the SQS ``Body`` (base64, then gzip-if-magic), verify the
    HMAC ``signature`` from the ``X-Signature`` message attribute, and
    return the parsed event.
    """
    inflated = decode_sqs_payload(message_body)
    return _verify_and_parse(inflated, signature, secret)


def verify_and_parse_sns(
    message: _BytesLike,
    signature: Union[str, bytes],
    secret: str,
) -> Dict[str, Any]:
    """Decode the SNS ``Message`` (identical to SQS handling), verify
    the HMAC ``signature`` from the ``X-Signature`` message attribute,
    and return the parsed event.
    """
    inflated = decode_sns_payload(message)
    return _verify_and_parse(inflated, signature, secret)
