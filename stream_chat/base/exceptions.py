import json
from typing import Dict


class StreamChannelException(Exception):
    pass


class InvalidWebhookError(Exception):
    """Invalid webhook signature or malformed gzip/base64/JSON envelope.

    Raised by :mod:`stream_chat.webhook` on any failure path: signature
    mismatch, malformed base64, gzip decompression failure, or invalid
    JSON payload. The message text identifies the failure mode so
    callers that want to differentiate (security logging, retry policy)
    can filter on substring or on the module-level constants.
    """


INVALID_WEBHOOK_SIGNATURE_MISMATCH = "signature mismatch"
INVALID_WEBHOOK_INVALID_BASE64 = "invalid base64 encoding"
INVALID_WEBHOOK_GZIP_FAILED = "gzip decompression failed"
INVALID_WEBHOOK_INVALID_JSON = "invalid JSON payload"


class StreamAPIException(Exception):
    def __init__(self, text: str, status_code: int) -> None:
        self.response_text = text
        self.status_code = status_code
        self.json_response = False

        try:
            parsed_response: Dict = json.loads(text)
            self.error_code = parsed_response.get("code", "unknown")
            self.error_message = parsed_response.get("message", "unknown")
            self.json_response = True
        except ValueError:
            pass

    def __str__(self) -> str:
        if self.json_response:
            return f'StreamChat error code {self.error_code}: {self.error_message}"'
        else:
            return f"StreamChat error HTTP code: {self.status_code}"
