from __future__ import annotations

import spice_rack

__all__ = (
    "User",
)


class User(spice_rack.pydantic_bases.AbstractValueModel):
    """internal model for a user"""
    name: str
    email: str
