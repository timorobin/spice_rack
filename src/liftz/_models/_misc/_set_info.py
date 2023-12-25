from __future__ import annotations
from pydantic import Field

from spice_rack import pydantic_bases


__all__ = (
    "PrescribedSet",
    "CompletedSet"
)


class PrescribedSet(pydantic_bases.AbstractValueModel):
    """info about an individual set"""
    weight: float = Field(description="the weight suggested")
    reps: int = Field(description="the reps suggested")


class CompletedSet(pydantic_bases.AbstractValueModel):
    """info about a completed set"""
    weight: float = Field(description="the weight used")
    reps: int = Field(description="the reps completed")
    notes: str = Field(description="free-form info about the set", default="no notes specified")
