from __future__ import annotations
import typing as t
import pydantic

__all__ = (
    "RootModel",
)


RootTV = t.TypeVar("RootTV", )


class RootModel(pydantic.RootModel[RootTV], t.Generic[RootTV]):
    """subclass pydantic's RootModel with no extra functionality at the moment"""
    ...
