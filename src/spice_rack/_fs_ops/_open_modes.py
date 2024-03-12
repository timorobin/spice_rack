from __future__ import annotations
import typing as t
from typing_extensions import TypeAlias
from io import TextIOWrapper
from fsspec.spec import AbstractBufferedFile


__all__ = (
    "SupportedOpenModesT",
    "OpenFileT"
)


SupportedOpenModesT: TypeAlias = t.Literal["ab", "wb", "rb"]
OpenFileT: TypeAlias = t.Union[AbstractBufferedFile, TextIOWrapper]
