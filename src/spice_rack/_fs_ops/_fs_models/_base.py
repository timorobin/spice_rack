from __future__ import annotations
import pathlib
from abc import abstractmethod
from devtools import pformat
import typing as t
import pydantic

from spice_rack import _bases, _logging
from spice_rack._fs_ops import (
    _path_strs,
    _file_systems,
)

if t.TYPE_CHECKING:
    from spice_rack._fs_ops._fs_models._file import FilePath
    from spice_rack._fs_ops._fs_models._dir import DirPath
    from spice_rack._fs_ops._fs_models._types import FileOrDirPathT


__all__ = (
    "AbstractFileSystemObj",
)


class AbstractFileSystemObj(
    _bases.DispatchableValueModelBase,
    _logging.log_extra.LoggableObjMixin
):
    """
    Base class for all file system objects in this package
    All file and dir objects inherit this class
    """
    path: _path_strs.FileOrDirAbsPathT
    file_system: _file_systems.AnyFileSystemT = pydantic.Field(
        description="the file system object for this file",
        default=None
    )

    @pydantic.model_validator(mode="before")
    def _handle_str(cls, data: t.Any) -> t.Any:
        if isinstance(data, (pathlib.Path, str)):
            data = cls.init_from_str(str(data)).model_dump()

        file_system_key = "file_system"
        path_key = "path"

        if isinstance(data, dict):
            raw_file_system = data.get(file_system_key)
            raw_path: str = data.get(path_key)
            if raw_path is None:
                raise ValueError(
                    f"no 'path' specified? data: \n{pformat(data)}"
                )
            else:
                raw_path = str(raw_path)
            file_system: _file_systems.AnyFileSystemT

            if raw_file_system is None:
                file_system = _file_systems.infer_file_system(raw_path)
            else:
                file_system = _file_systems.AnyFileSystemTypeAdapter.validate_python(
                    raw_file_system
                )
            data["file_system"] = file_system

            # either way we want to clean the path
            # either way we clean the path
            path_formatted = file_system.clean_raw_path_str(raw_path)
            data[file_system_key] = file_system
            data[path_key] = path_formatted

        return data

    @property
    def file_system_type(self) -> _bases.dispatchable.ClassId:
        """get the class id of the file system tied to this path object"""
        return self.file_system.get_class_id()

    @t.final
    def exists(self) -> bool:
        """
        returns True if this file system object exists, false otherwise
        """
        return self.file_system.exists(self.path)

    def __repr__(self) -> str:
        """
        deprecated, we want to remove all usage of this
        in logging and error messaging and use special_repr only
        """
        return self.special_repr()

    def __hash__(self) -> int:
        return hash(
            (self.path, self.file_system)
        )

    @abstractmethod
    def _special_repr_short(self) -> str:
        ...

    @abstractmethod
    def _special_repr_verbose(self) -> str:
        ...

    @t.final
    def special_repr(self, verbose: bool = False) -> str:
        if verbose:
            return self._special_repr_verbose()
        else:
            return self._special_repr_short()

    def __eq__(self, other: AbstractFileSystemObj) -> bool:
        if type(self) == type(other):  # noqa
            if hash(self) == hash(other):
                return True
        return False

    @abstractmethod
    def delete(
            self,
            if_non_existent: t.Literal["raise", "return"] = "return"
    ) -> None:
        ...

    @t.overload
    def build_like(self, path: _path_strs.AbsoluteFilePathStr) -> FilePath:
        ...

    @t.overload
    def build_like(self, path: _path_strs.AbsoluteDirPathStr) -> DirPath:
        ...

    @t.overload
    def build_like(self, path: str) -> FileOrDirPathT:
        ...

    def build_like(
            self, path: t.Union[str, _path_strs.AbsoluteFilePathStr, _path_strs.AbsoluteDirPathStr]
    ) -> FileOrDirPathT:
        """build a new file or dir path instance using the specified file path and the file
        system tied to this instance
        """
        from spice_rack._fs_ops._fs_models._file import FilePath
        from spice_rack._fs_ops._fs_models._dir import DirPath

        parsed_path = _path_strs.FileOrDirAbsPathTypeAdapter.validate_python(
            path
        )
        if isinstance(parsed_path, _path_strs.AbsoluteFilePathStr):
            return FilePath(
                path=parsed_path,
                file_system=self.file_system
            )
        elif isinstance(parsed_path, _path_strs.AbsoluteDirPathStr):
            return DirPath(
                path=parsed_path,
                file_system=self.file_system
            )
        else:
            raise ValueError(
                f"'{parsed_path}' is type {type(parsed_path)} which is unexpected"
            )

    def get_parent(self) -> DirPath:
        """return the dir path instance of the parent
        of the current dir or file path instance"""
        parent_path = self.path.get_parent()
        return self.build_like(path=parent_path)

    @abstractmethod
    def get_name(self) -> str:
        """get simple name, i.e. the most terminal chunk in the path"""
        ...

    def ensure_exists(self) -> None:
        """raise error if the path doesn't exist"""
        self.file_system.ensure_exists(self.path)

    def ensure_nonexistent(self) -> None:
        """raise an error if the path does exist"""
        self.file_system.ensure_nonexistent(self.path)

    def as_str(self) -> str:
        """
        return a contextualized str representation of the path,
        meaning the file system-specific prefix is used.
        """
        return self.file_system.contextualize_abs_path(self.path)

    def __get_logger_data__(self) -> t.Dict:
        return {
            "type": self.__class__.__name__,  # noqa
            "path": self.as_str(),
            "file_system_info": self.file_system.__get_logger_data__()
        }

    @classmethod
    @abstractmethod
    def init_from_str(cls, raw_str: str) -> AbstractFileSystemObj:
        ...
