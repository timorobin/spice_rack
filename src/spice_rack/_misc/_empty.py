from __future__ import annotations
from typing import Literal
from typing_extensions import TypeAlias

from pydantic import BaseModel, Field


__all__ = (
    "EMPTY",
    "EmptyT"
)


class _Empty(BaseModel):
    """
    class to represent a null, always used as a default.
    This is validated as a pydantic field annotation, or within one.
    """
    __root__: Literal[
        "EMPTY_0c616003538843f2a01f9d6029a3ea65"
    ] = Field(
        description="ignore this value",
        default="EMPTY_0c616003538843f2a01f9d6029a3ea65",
        const=True
    )

    def __hash__(self) -> int:
        return hash("EMPTY_0c616003538843f2a01f9d6029a3ea65")


EMPTY = _Empty()

EmptyT: TypeAlias = _Empty
