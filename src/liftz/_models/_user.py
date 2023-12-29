from __future__ import annotations
from pydantic import Field

import spice_rack

__all__ = (
    "User",
)


UserId = spice_rack.guid.GuidStr


class User(spice_rack.pydantic_bases.AbstractValueModel):
    """internal model for a user"""
    user_id: UserId = Field(description="the user id", default_factory=UserId.generate)
    name: str
    email: str
