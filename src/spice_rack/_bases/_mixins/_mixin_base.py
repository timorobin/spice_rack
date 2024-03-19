from __future__ import annotations

from spice_rack._bases._base_base import PydanticBase


__all__ = ("PydanticMixinBase", )


class PydanticMixinBase(PydanticBase):
    """
    Base for a class intended to be used purely as a mixin to augment another pydantic model.
    Primarily this is meant to add fields to another model.
    No special behavior is implemented, and this inherits from pydantic's BaseModel
    and behaves as a regular pydantic class. We will circle back and add checks, but for
    now the extra layer of inheritance can at least serve as a visual call out about a given
    mixin class.
    """
    ...
