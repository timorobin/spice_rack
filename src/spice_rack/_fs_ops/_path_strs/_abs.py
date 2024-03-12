from __future__ import annotations
from abc import abstractmethod
import typing as t
from pathlib import Path

from spice_rack._fs_ops._path_strs import _base, _rel

__all__ = (
    "AbsoluteFilePathStr",
    "AbsoluteDirPathStr",
    "AnyAbsPathT"
)


class _AbstractAbsolutePathStr(_base.AbstractPathStr):
    """Base class for an absolute file path and absolute dir path string classes"""
    @abstractmethod
    def get_name(self) -> str:
        ...

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        root_data = super()._format_str_val(root_data)
        if not root_data.startswith("/"):
            raise ValueError(
                f"'{root_data}' is relative so it is not a valid absolute path"
            )
        return root_data

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
    def _format_str_val(cls, root_data: str) -> str:
        root_data = super()._format_str_val(root_data)
        if root_data.endswith("/"):
            raise ValueError(
                f"'{root_data}' ends with '/' so it is not a file path"
            )
        return root_data

    def get_name(self, include_suffixes: bool = False) -> str:
        """get simple name, i.e. the most terminal chunk in the path"""
        name_w_suffixes = str(self).split("/")[-1]
        if include_suffixes:
            return name_w_suffixes
        else:
            return name_w_suffixes.split(".")[0]

    # def get_suffixes(self) -> list[_special_types.FileExt]:
    #     suffixes = str(self).split(".")[1:]
    #     return [
    #         _special_types.FileExt(suffix) for suffix in suffixes
    #     ]
    #
    # def get_file_ext(self) -> Optional[_special_types.FileExt]:
    #     suffixes = self.get_suffixes()
    #     if suffixes:
    #         return suffixes[-1]
    #     else:
    #         return None
    #
    # def get_mime_type(self) -> Optional[_special_types.MimeType]:
    #     file_ext = self.get_file_ext()
    #     if file_ext:
    #         mime_type_maybe = file_ext.get_mime_type()
    #         return mime_type_maybe
    #     else:
    #         return None


@t.final
class AbsoluteDirPathStr(_AbstractAbsolutePathStr):
    """subclasses string to enforce constraints on the dir path str for a dir path object"""

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        root_data = super()._format_str_val(root_data)
        if not root_data.endswith("/"):

            # if no extensions, we'll treat as dir anyway
            if not Path(root_data).suffix:
                root_data = root_data + "/"
            else:
                raise ValueError(
                    f"'{root_data}' is not a directory path"
                )
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
    def joinpath(self, rel_path: str) -> AnyAbsPathT:
        ...

    def joinpath(
            self,
            rel_path: t.Union[str, _rel.AnyRelPathT]
    ) -> AnyAbsPathT:
        rel_path_parsed: _rel.AnyRelPathT
        try:
            rel_path_parsed = _rel.RelDirPathStr(rel_path)

        except ValueError:
            rel_path_parsed = _rel.RelFilePathStr(rel_path)

        except Exception as e:
            raise e

        extended_path_raw: str = str(self) + str(rel_path_parsed)

        if isinstance(rel_path_parsed, _rel.RelFilePathStr):
            extended_path = AbsoluteFilePathStr(extended_path_raw)

        elif isinstance(rel_path_parsed, _rel.RelDirPathStr):
            extended_path = AbsoluteDirPathStr(extended_path_raw)

        else:
            raise TypeError(f"{type(rel_path_parsed)} unexpected")

        return extended_path


AnyAbsPathT = t.Union[AbsoluteFilePathStr, AbsoluteDirPathStr]
