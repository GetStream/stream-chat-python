from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class RateLimitInfo:
    limit: int
    remaining: int
    reset: datetime

    def as_dict(self) -> Dict[str, int]:
        return asdict(self)
