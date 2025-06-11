from datetime import datetime
from typing import Optional, TypedDict


class SharedLocationsOptions(TypedDict):
    longitude: Optional[int]
    latitude: Optional[int]
    end_at: Optional[datetime]
