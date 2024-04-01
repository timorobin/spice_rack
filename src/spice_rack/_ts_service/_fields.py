from __future__ import annotations
import typing as t
import pydantic

from spice_rack._ts_service._timestamp import Timestamp


__all__ = (
    "CreatedAtFieldAnn",
    "CreatedAtWithDefaultFieldAnn"
)


CreatedAtFieldAnn = t.Annotated[
    Timestamp,
    pydantic.Field(
        description="the timestamp when this object was created",
    )
]


CreatedAtWithDefaultFieldAnn = t.Annotated[
    Timestamp,
    pydantic.Field(
        description="the timestamp when this object was created, if not specified, "
                    "we'll create a timestamp at current time",
        default_factory=Timestamp.now
    )
]
