from __future__ import annotations
from abc import abstractmethod
from typing import ClassVar, Type
from pydantic import Field

from spice_rack import guid, pydantic_bases


__all__ = (
    "RecordMixin",
    "RecordRef"
)


class RecordMixin(guid.GuidMixin):
    """this mixin contains standard stuff to make a class persistable in our repo"""
    @classmethod
    @abstractmethod
    def get_repo_name(cls) -> str:
        ...


class RecordRef(pydantic_bases.AbstractValueModel):
    _repo_name: ClassVar[str]
    guid: guid.GuidStr = Field(description="the guid for the reference")

    def __class_getitem__(cls, item: Type[RecordMixin]):
        if not issubclass(item, RecordMixin):
            raise ValueError(f"'{item}' isn't a record mixin")
        cls._repo_name = item.get_repo_name()
