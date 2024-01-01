from __future__ import annotations

from pydantic import BaseModel


__all__ = (
    "PydanticMixinBase",
)


class PydanticMixinBase(BaseModel):
    """
    base class for creating a mixin class that adds fields to
    a pydantic model. Only fields are meant to be defined on subclasses
    of this class.
    """
    ...
