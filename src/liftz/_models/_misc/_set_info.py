from __future__ import annotations

from spice_rack import pydantic_bases


__all__ = (
    "SetInfo",
)


class SetInfo(pydantic_bases.AbstractValueModel):
    """info about an individual set"""
    weight: float
    reps: int
