from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RateLimitInfo:
    limit: int
    remaining: int
    reset: datetime
