from __future__ import annotations
import uuid
from typing import Any
from pydantic import Field

from spice_rack import base_classes, pydantic_bases

__all__ = (
    "GuidStr",
    "GuidMixin"
)


class GuidStr(base_classes.AbstractSpecialStr):
    """a hex of a UUID4 object"""

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        try:
            uuid_obj = uuid.UUID(hex=root_data, version=4)
        except Exception as e:
            raise ValueError(
                f"failed to parse the raw str as a UUID4, '{root_data}'"
            )
        return uuid_obj.hex

    @classmethod
    def _parse_non_str(cls, root_data: Any) -> str:
        if isinstance(root_data, uuid.UUID):
            return root_data.hex
        else:
            super()._parse_non_str(root_data)

    @classmethod
    def generate(cls) -> GuidStr:
        return GuidStr(uuid.uuid4().hex)


class GuidMixin(pydantic_bases.PydanticMixinBase):
    guid: GuidStr = Field(
        description="globally unique id as a string",
        default_factory=GuidStr.generate
    )
