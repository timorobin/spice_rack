from __future__ import annotations
from abc import ABC

from typing_extensions import TypeAlias


__all__ = (
    "ClassName",
    "ClassNameMixin"
)


ClassName: TypeAlias = str


class ClassNameMixin(ABC):
    @classmethod
    def get_cls_name(cls) -> ClassName:
        return ClassName(cls.__name__)
