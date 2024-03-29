from __future__ import annotations
from abc import abstractmethod
import typing as t
from pathlib import Path
import pydantic

from spice_rack._fs_ops._path_strs import _base, _rel, _path_checkers
from spice_rack._fs_ops import _file_info


__all__ = (
    "AbsoluteFilePathStr",
    "AbsoluteDirPathStr",
    "FileOrDirAbsPathT",
    "FileOrDirAbsPathTypeAdapter"
)


class _AbstractAbsolutePathStr(_base.AbstractPathStr):
    """Base class for an absolute file path and absolute dir path string classes"""
    @abstractmethod
    def get_name(self) -> str:
        ...

    @classmethod
    def _check_str_val(cls, __raw_str: str) -> t.List[str]:
        issues = super()._check_str_val(__raw_str)
        issues.extend(_path_checkers.abs_validator(__raw_str))
        return issues

    def get_parent(self) -> AbsoluteDirPathStr:
        parent_path_raw = str(Path(str(self)).parent)
        if not parent_path_raw.endswith("/"):
            parent_path_raw = parent_path_raw + "/"
        return AbsoluteDirPathStr(parent_path_raw)


@t.final
class AbsoluteFilePathStr(_AbstractAbsolutePathStr):
    """
    This represents an absolute file path string. It must start with a backslash and must not end
    with a backslash.
    """
    @classmethod
    def _check_str_val(cls, __raw_str: str) -> t.List[str]:
        issues = super()._check_str_val(__raw_str)
        issues.extend(_path_checkers.file_validator(__raw_str))
        return issues

    def get_name(self, include_suffixes: bool = False) -> str:
        """get simple name, i.e. the most terminal chunk in the path"""
        name_w_suffixes = str(self).split("/")[-1]
        if include_suffixes:
            return name_w_suffixes
        else:
            return name_w_suffixes.split(".")[0]

    def get_suffixes(self) -> list[_file_info.FileExt]:
        suffixes = str(self).split(".")[1:]
        return [
            _file_info.FileExt(suffix) for suffix in suffixes
        ]

    def get_file_ext(self) -> t.Optional[_file_info.FileExt]:
        suffixes = self.get_suffixes()
        if suffixes:
            return suffixes[-1]
        else:
            return None

    def get_mime_type(self) -> t.Optional[_file_info.MimeType]:
        file_ext = self.get_file_ext()
        if file_ext:
            mime_type_maybe = file_ext.get_mime_type()
            return mime_type_maybe
        else:
            return None


@t.final
class AbsoluteDirPathStr(_AbstractAbsolutePathStr):
    """subclasses string to enforce constraints on the dir path str for a dir path object"""

    @classmethod
    def _check_str_val(cls, __raw_str: str) -> t.List[str]:
        issues = super()._check_str_val(__raw_str)
        issues.extend(_path_checkers.dir_validator(__raw_str))
        return issues

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        root_data = super()._format_str_val(root_data)
        if not root_data.endswith("/"):
            root_data = root_data + "/"
        return root_data

    def get_name(self) -> str:
        """get simple name, i.e. the most terminal chunk in the path"""
        return str(self).split("/")[-2] + "/"

    @t.overload
    def joinpath(self, rel_path: _rel.RelDirPathStr) -> AbsoluteDirPathStr:
        ...

    @t.overload
    def joinpath(self, rel_path: _rel.RelFilePathStr) -> AbsoluteFilePathStr:
        ...

    @t.overload
    def joinpath(self, rel_path: str) -> FileOrDirAbsPathT:
        ...

    def joinpath(
            self,
            rel_path: t.Union[str, _rel.FileOrDirRelPathT]
    ) -> FileOrDirAbsPathT:
        rel_path_parsed: _rel.FileOrDirRelPathT
        rel_path_parsed = _rel.FileOrDirRelPathTypeAdapter.validate_python(
            rel_path
        )
        extended_path_raw: str = str(self) + str(rel_path_parsed)

        if isinstance(rel_path_parsed, _rel.RelFilePathStr):
            extended_path = AbsoluteFilePathStr(extended_path_raw)

        elif isinstance(rel_path_parsed, _rel.RelDirPathStr):
            extended_path = AbsoluteDirPathStr(extended_path_raw)

        else:
            raise TypeError(f"{type(rel_path_parsed)} unexpected")

        return extended_path


_TagsT = t.Literal["dir", "file"]


def _discrim(raw_str: str) -> _TagsT:
    if raw_str.endswith("/"):
        return "dir"
    else:
        return "file"


FileOrDirAbsPathT = t.Annotated[
    t.Union[
        t.Annotated[AbsoluteFilePathStr, pydantic.Tag("file")],
        t.Annotated[AbsoluteDirPathStr, pydantic.Tag("dir")],
    ],
    pydantic.Discriminator(_discrim)
]


FileOrDirAbsPathTypeAdapter: pydantic.TypeAdapter[FileOrDirAbsPathT] = pydantic.TypeAdapter(
    FileOrDirAbsPathT
)
