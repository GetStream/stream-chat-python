"""Helpers for verifying and decoding outbound Stream webhook payloads.

Stream Chat can compress outbound webhook payloads with gzip and, for SQS / SNS
firehose delivery, also wrap the compressed bytes in base64 so they remain
valid UTF-8 over the queue. The helpers in this module mirror the cross-SDK
contract: callers can either decode the body without checking the signature
(:func:`decompress_webhook_body`) or do decode + HMAC verification in one call
(:func:`verify_and_decode_webhook`).

The functions live outside the client classes so they can be exercised in
isolation, without instantiating an HTTP client. The client methods just
delegate here, passing ``self.api_secret``.
"""

import base64
import gzip
import hashlib
import hmac
from typing import Optional, Union

from stream_chat.base.exceptions import WebhookSignatureError

_BASE64_ALIASES = frozenset({"base64", "b64"})
_GZIP_ALIASES = frozenset({"gzip"})


def _to_bytes(body: Union[bytes, str]) -> bytes:
    if isinstance(body, str):
        return body.encode("utf-8")
    if isinstance(body, (bytes, bytearray, memoryview)):
        return bytes(body)
    raise TypeError(f"webhook body must be bytes or str, got {type(body).__name__}")


def _normalize(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.strip().lower()


def decompress_webhook_body(
    body: Union[bytes, str],
    content_encoding: Optional[str] = None,
    payload_encoding: Optional[str] = None,
) -> bytes:
    """Decode a (possibly wrapped + compressed) webhook payload.

    Application order:

    1. ``payload_encoding`` (``"base64"`` / ``"b64"``) is unwrapped first.
       This corresponds to the SQS / SNS envelope, which base64-wraps the
       compressed bytes so they stay valid UTF-8 over the queue.
    2. ``content_encoding`` (``"gzip"``) is decompressed.
    3. The resulting raw JSON bytes are returned. The caller can decode them
       as UTF-8 or pass them straight to :func:`json.loads` (which accepts
       bytes).

    ``None`` or an empty string for either encoding is a no-op, so the regular
    HTTP webhook path (no compression, no wrapping) is just an identity
    function and stays bytewise identical to today.

    :param body: raw bytes or str received from Stream
    :param content_encoding: value of the ``Content-Encoding`` header (``"gzip"``)
    :param payload_encoding: wrapper around the compressed bytes
        (``"base64"`` / ``"b64"``)
    :returns: the uncompressed JSON body as bytes
    :raises WebhookSignatureError: when the body cannot be decoded with the
        requested encodings
    :raises ValueError: when an encoding value is not supported by this SDK
    """
    data = _to_bytes(body)

    payload_enc = _normalize(payload_encoding)
    if payload_enc:
        if payload_enc in _BASE64_ALIASES:
            try:
                data = base64.b64decode(data, validate=True)
            except ValueError as exc:
                raise WebhookSignatureError(
                    f"failed to decode webhook body with payload_encoding={payload_enc!r}: {exc}"
                )
        else:
            raise ValueError(
                f"unsupported webhook payload_encoding: {payload_encoding}. "
                "This SDK only supports base64."
            )

    content_enc = _normalize(content_encoding)
    if content_enc:
        if content_enc in _GZIP_ALIASES:
            try:
                data = gzip.decompress(data)
            except (gzip.BadGzipFile, OSError, EOFError) as exc:
                raise WebhookSignatureError(
                    f"failed to decompress webhook body with Content-Encoding={content_enc!r}: {exc}"
                )
        else:
            raise ValueError(
                f"unsupported webhook Content-Encoding: {content_encoding}. "
                "This SDK only supports gzip; set webhook_compression_algorithm "
                'to "gzip" on the app config.'
            )

    return data


def verify_and_decode_webhook(
    body: Union[bytes, str],
    x_signature: Union[str, bytes],
    api_secret: str,
    content_encoding: Optional[str] = None,
    payload_encoding: Optional[str] = None,
) -> bytes:
    """Decode a webhook payload and verify its HMAC-SHA256 signature.

    The signature is always computed over the **uncompressed** JSON bytes,
    so this helper first applies :func:`decompress_webhook_body` and then
    compares the digest with ``x_signature`` using :func:`hmac.compare_digest`.

    :returns: the verified, uncompressed JSON body as bytes
    :raises WebhookSignatureError: on signature mismatch or any decode error
    """
    decoded = decompress_webhook_body(
        body, content_encoding=content_encoding, payload_encoding=payload_encoding
    )

    if isinstance(x_signature, bytes):
        x_signature = x_signature.decode()

    expected = hmac.new(
        key=api_secret.encode(), msg=decoded, digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, x_signature):
        raise WebhookSignatureError("invalid webhook signature")

    return decoded
