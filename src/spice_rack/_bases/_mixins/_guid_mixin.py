from __future__ import annotations
import uuid
import pydantic

__all__ = ("GuidMixin", )


class GuidMixin(pydantic.BaseModel):
    """
    adds a UUID4 field, 'guid' that is an uuid4 object
    """
    guid: pydantic.UUID4 = pydantic.Field(
        description="globally unique id field",
        default_factory=uuid.uuid4
    )
