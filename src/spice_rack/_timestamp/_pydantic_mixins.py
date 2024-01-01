from __future__ import annotations
from pydantic import Field

from spice_rack import _base_classes
from spice_rack._timestamp._timestamp import Timestamp


__all__ = (
    "CreatedAtMixin",
)


class CreatedAtMixin(_base_classes.pydantic.PydanticMixinBase):
    """adds a 'created_at' field"""
    created_at: Timestamp = Field(
        description="The timestamp when this object was created",
        default_factory=Timestamp.now
    )
