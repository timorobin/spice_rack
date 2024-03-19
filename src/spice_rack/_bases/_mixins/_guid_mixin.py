from __future__ import annotations
import uuid
import pydantic

from spice_rack._bases._mixins._mixin_base import PydanticMixinBase

__all__ = ("GuidMixin", )


class GuidMixin(PydanticMixinBase):
    """
    adds a UUID4 field, 'guid' that is an uuid4 object
    """
    guid: pydantic.UUID4 = pydantic.Field(
        description="globally unique id field",
        default_factory=uuid.uuid4
    )
