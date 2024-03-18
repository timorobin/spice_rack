from __future__ import annotations

from spice_rack import _bases


__all__ = (
    "FileExt",
)


class FileExt(_bases.special_str.SpecialStrBase):
    """formats a file ext to make working with them more convenient"""

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        if root_data.startswith("."):
            root_data = root_data[1:]
        return root_data

    def with_dot_prefix(self) -> str:
        return f".{self}"

    def __eq__(self, other: str) -> bool:
        return str(self) == str(FileExt(other))
