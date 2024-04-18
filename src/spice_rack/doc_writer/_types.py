from __future__ import annotations
import typing as t
import pydantic

from spice_rack import _bases, _fs_ops


__all__ = (
    "HeaderLine",
)


class HeaderLine(_bases.ValueModelBase):
    """a special subtype of string denoting this is a head"""
    text: str
    level: int


class HeaderFormatterProtocol(t.Protocol):
    def format(self, header: HeaderLine) -> str:
        ...


class UnderlineFormatter(_bases.ValueModelBase):
    sep_char: str = "-"

    def format(self, header: HeaderLine) -> str:
        return header.text + "\n" + len(header.text) * self.sep_char


class OverAndUnderLineFormatter(_bases.ValueModelBase):
    sep_char: str = "-"
    def format(self, header: HeaderLine) -> str:
        line =  len(header.text) * self.sep_char
        return line + "\n" + header.text + "\n" + line


class HeaderSepConfig(_bases.ValueModelBase):
    level: int
    formatter: HeaderFormatterProtocol



class Doc(_bases.RootModel[t.List[t.Union[HeaderLine, str]]]):

    def format_contents(self, header_seps: t.Dict[int, ""]) -> str:



    def write(self, file_path: _fs_ops.FilePath) -> None:
        ...

