from __future__ import annotations
from typing import Any, Sequence, ClassVar, Iterator

from spice_rack._base_classes import _special_types


__all__ = (
    "ClassIdName",
    "ClassIdPath"
)


class ClassIdName(_special_types.special_str_base.AbstractSpecialStr):
    """the name of the class, built from the class name"""

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data


class ClassIdPath(_special_types.special_str_base.AbstractSpecialStr):
    """a path of class names"""
    _sep: ClassVar[str] = "."

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data

    @classmethod
    def _parse_non_str(cls, root_data: Any) -> str:
        if isinstance(root_data, Sequence):
            pieces: list[ClassIdName] = [ClassIdName(part) for part in root_data]
            single_str = cls._sep.join(pieces)
            return single_str
        else:
            return super()._parse_non_str(root_data)

    def iter_parts(self) -> Iterator[ClassIdName]:
        for part in self.split(self._sep):
            yield ClassIdName(part)

    def joinpath(self, class_id: ClassIdName) -> ClassIdPath:
        parts = list(self.iter_parts())
        parts.append(class_id)
        return ClassIdPath(parts)
