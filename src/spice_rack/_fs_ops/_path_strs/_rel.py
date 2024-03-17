from __future__ import annotations
from abc import abstractmethod
import typing as t
from pathlib import Path
import pydantic

from spice_rack._fs_ops._path_strs import _base, _path_checkers
from spice_rack._fs_ops import _file_ext


__all__ = (
    "RelFilePathStr",
    "RelDirPathStr",
    "FileOrDirRelPathT",
    "FileOrDirRelPathTypeAdapter"
)


class _AbstractRelPathStr(_base.AbstractPathStr):
    """Base class for a relative file path and relative dir path string classes"""
    @abstractmethod
    def get_name(self) -> str:
        ...

    @classmethod
    def _check_str_val(cls, __raw_str: str) -> t.List[str]:
        issues = super()._check_str_val(__raw_str)
        issues.extend(_path_checkers.rel_validator(__raw_str))
        return issues

    def get_parent(self) -> RelDirPathStr:
        parent_path_raw = str(Path(str(self)).parent)
        if not parent_path_raw.endswith("/"):
            parent_path_raw = parent_path_raw + "/"
        return RelDirPathStr(parent_path_raw)


@t.final
class RelFilePathStr(_AbstractRelPathStr):
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

    def get_suffixes(self) -> list[_file_ext.FileExt]:
        suffixes = str(self).split(".")[1:]
        return [
            _file_ext.FileExt(suffix) for suffix in suffixes
        ]

    def get_file_ext(self) -> t.Optional[_file_ext.FileExt]:
        suffixes = self.get_suffixes()
        if suffixes:
            return suffixes[-1]
        else:
            return None

    # def get_mime_type(self) -> Optional[_special_types.MimeType]:
    #     file_ext = self.get_file_ext()
    #     if file_ext:
    #         mime_type_maybe = file_ext.get_mime_type()
    #         return mime_type_maybe
    #     else:
    #         return None


@t.final
class RelDirPathStr(_AbstractRelPathStr):
    """subclasses string to enforce constraints on the dir path str"""

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
    def joinpath(self, rel_path: RelDirPathStr) -> RelDirPathStr:
        ...

    @t.overload
    def joinpath(self, rel_path: RelFilePathStr) -> RelFilePathStr:
        ...

    @t.overload
    def joinpath(self, rel_path: str) -> FileOrDirRelPathT:
        ...

    def joinpath(
            self,
            rel_path: t.Union[str, FileOrDirRelPathT]
    ) -> FileOrDirRelPathT:
        rel_path_parsed: FileOrDirRelPathT
        try:
            rel_path_parsed = RelDirPathStr(rel_path)

        except ValueError:
            rel_path_parsed = RelFilePathStr(rel_path)

        except Exception as e:
            raise e

        extended_path_raw: str = str(self) + str(rel_path_parsed)

        if isinstance(rel_path_parsed, RelFilePathStr):
            extended_path = RelFilePathStr(extended_path_raw)

        elif isinstance(rel_path_parsed, RelDirPathStr):
            extended_path = RelDirPathStr(extended_path_raw)

        else:
            raise TypeError(f"{type(rel_path_parsed)} unexpected")

        return extended_path


_TagsT = t.Literal["dir", "file"]


def _discrim(raw_str: str) -> _TagsT:
    if raw_str.endswith("/"):
        return "dir"
    else:
        return "file"


FileOrDirRelPathT = t.Annotated[
    t.Union[
        t.Annotated[RelFilePathStr, pydantic.Tag("file")],
        t.Annotated[RelDirPathStr, pydantic.Tag("dir")],
    ],
    pydantic.Discriminator(_discrim)
]


FileOrDirRelPathTypeAdapter = pydantic.TypeAdapter(FileOrDirRelPathT)
