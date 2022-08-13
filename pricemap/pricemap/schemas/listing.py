from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class Listing(BaseModel):
    """_summary_ : This is the base model for a user."""

    listing_id: Optional[int] = None
    place_id: Optional[int] = None
    price: Optional[int] = None
    area: Optional[int] = None
    room_count: Optional[int] = None
    seen_at: Optional[datetime] = None