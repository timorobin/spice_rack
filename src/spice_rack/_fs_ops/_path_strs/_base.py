from __future__ import annotations
import typing as t
from abc import abstractmethod
from pathlib import Path

from spice_rack import _bases


__all__ = (
    "AbstractPathStr",
)


class AbstractPathStr(_bases.special_str.SpecialStrBase):
    """Base class for all path string classes"""
    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        return root_data

    @classmethod
    def _parse_non_str(cls, root_data: t.Any) -> str:
        if isinstance(root_data, Path):
            str_val: str = str(root_data)

            try:
                if root_data.is_dir():
                    if not str_val.endswith("/"):
                        str_val += "/"

            # might have permissions issue with the path, but that is ok
            except Exception:  # noqa
                pass

            return str_val
        else:
            return super()._parse_non_str(root_data)

    @classmethod
    def get_cls_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def get_name(self) -> str:
        """get simple name, i.e. the most terminal chunk in the path"""
        ...

    @abstractmethod
    def get_parent(self) -> AbstractPathStr:
        ...
