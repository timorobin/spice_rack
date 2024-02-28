from __future__ import annotations
from typing import Literal
from typing_extensions import TypeAlias

from pydantic import RootModel


__all__ = (
    "EMPTY",
    "EmptyT"
)


class _Empty(RootModel):
    """
    class to represent a null, always used as a default.
    This is validated as a pydantic field annotation, or within one.
    """
    root: Literal[
        "EMPTY_0c616003538843f2a01f9d6029a3ea65"
    ] = "EMPTY_0c616003538843f2a01f9d6029a3ea65"

    def __hash__(self) -> int:
        return hash("EMPTY_0c616003538843f2a01f9d6029a3ea65")


EMPTY = _Empty()

EmptyT: TypeAlias = _Empty
