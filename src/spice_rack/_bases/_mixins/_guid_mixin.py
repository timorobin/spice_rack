from __future__ import annotations
import pydantic

from spice_rack._bases._mixins._mixin_base import PydanticMixinBase
from spice_rack import _guid_service

__all__ = ("GuidMixin", )


class GuidMixin(PydanticMixinBase):
    """
    adds a UUID4 field, 'guid' that is an uuid4 object
    """
    guid: _guid_service.GuidT = pydantic.Field(
        description="globally unique id field",
        default_factory=_guid_service.gen_guid
    )
