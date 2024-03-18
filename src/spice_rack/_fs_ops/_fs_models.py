from __future__ import annotations
from abc import abstractmethod
from devtools import pformat
import typing as t
import pydantic

from spice_rack import _bases, _logging
from spice_rack._fs_ops import (
    _path_strs,
    # _exceptions,
    _file_systems,
    _helpers,
    _open_modes,
    _file_ext
)

__all__ = (
    "FilePath", "DirPath",
    "FileOrDirPathT", "FileOrDirPathTypeAdapter"
)


class _AbstractFileSystemObj(
    _bases.dispatchable.DispatchableValueModelBase,
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
    def _model_setup(cls, data: t.Any) -> t.Any:
        if isinstance(data, str):
            return cls.init_from_str(data)

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
                file_system = _helpers.infer_file_system(raw_path)
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
        return self.file_system.class_id

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

    def __eq__(self, other: _AbstractFileSystemObj) -> bool:
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

    def build_file_like(
            self,
            path: _path_strs.AbsoluteFilePathStr
    ) -> FilePath:
        return FilePath(
            path=path, file_system=self.file_system
        )

    def build_dir_like(
            self,
            path: _path_strs.AbsoluteDirPathStr
    ) -> DirPath:
        return DirPath(
            path=path, file_system=self.file_system
        )

    def build_like(
            self,
            path: t.Union[str, _path_strs.FileOrDirAbsPathT]
    ) -> t.Union[FilePath, DirPath]:
        path = _path_strs.FileOrDirAbsPathTypeAdapter.validate_python(path)
        if isinstance(path, _path_strs.AbsoluteDirPathStr):
            return self.build_dir_like(path=path)
        elif isinstance(path, _path_strs.AbsoluteFilePathStr):
            return self.build_file_like(path=path)
        else:
            raise ValueError(
                f"unexpected path type. {type(path)}, path: '{path}'"
            )

    def get_parent(self) -> DirPath:
        parent_path = self.path.get_parent()
        return self.build_dir_like(path=parent_path)

    @abstractmethod
    def get_name(self) -> str:
        """get simple name, i.e. the most terminal chunk in the path"""
        ...

    def ensure_exists(self) -> None:
        self.file_system.ensure_exists(self.path)

    def as_str(self) -> str:
        return self.file_system.contextualize_abs_path(self.path)

    def __get_logger_data__(self) -> t.Dict:
        return {
            "type": self.__class__.__name__,  # noqa
            "path": self.as_str(),
            "file_system_info": self.file_system.__get_logger_data__()
        }

    @classmethod
    @abstractmethod
    def init_from_str(cls, raw_str: str) -> _AbstractFileSystemObj:
        ...


class FilePath(_AbstractFileSystemObj):
    """
    this class represents a file on a file system,
    with the absolute full path string, and the file system instance
    """
    path: _path_strs.AbsoluteFilePathStr

    def _special_repr_short(self) -> str:
        return f"File[path='{self.path}', file_system_type={self.file_system.special_repr()}]"

    def _special_repr_verbose(self) -> str:
        return f"File[path='{self.path}', file_system_type={self.file_system.special_repr()}]"

    def delete(
            self,
            if_non_existent: t.Literal["raise", "return"] = "return",
    ) -> None:
        try:
            return self.file_system.delete_file(
                path=self.path,
                if_non_existent=if_non_existent
            )
        except Exception as e:
            raise e
        #
        # except _exceptions.FileSystemException as e:
        #     raise e
        # except Exception as e:
        #     raise _exceptions.FileSystemException(
        #         file_system=self.file_system,
        #         extra_info={
        #             "path": self.path,
        #             "error_type": type(e).__name__,
        #             "error_detail": str(e)
        #         }
        #     )

    def open(
            self,
            mode: _open_modes.SupportedOpenModesT = "rb"
    ) -> _open_modes.OpenFileT:
        try:
            return self.file_system.open_file(
                path=self.path,
                mode=mode
            )
        except Exception as e:
            raise e
        #
        # except _exceptions.FileSystemException as e:
        #     raise e
        # except Exception as e:
        #     raise _exceptions.FileSystemException(
        #         file_system=self.file_system,
        #         extra_info={
        #             "path": self.path,
        #             "error_type": type(e).__name__,
        #             "error_detail": str(e)
        #         }
        #     )

    def get_name(self, include_suffixes: bool = False) -> str:
        return self.path.get_name(include_suffixes=include_suffixes)

    def download_locally(
            self,
            dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteFilePathStr:
        return self.file_system.download_file_locally(
            path=self.path,
            dest_dir=dest_dir
        )

    def ensure_correct_file_ext(self, choices: list[str]) -> None:
        choices = [
            _file_ext.FileExt(choice) for choice in choices
        ]
        self.file_system.ensure_correct_file_ext(self.path, choices=choices)
    #
    # def ensure_correct_mime_type(self, choices: list[str]) -> None:
    #     choices = [
    #         _file_ext.MimeType(choice) for choice in choices
    #     ]
    #     self.file_system.ensure_correct_mime_type(self.path, choices=choices)

    @classmethod
    def init_from_str(cls, raw_str: str) -> FilePath:
        file_path = _path_strs.AbsoluteFilePathStr(raw_str)
        return FilePath(path=file_path)


class DirPath(_AbstractFileSystemObj):
    """
    this class represents a directory on a file system,
    with the absolute full path string, and the file system instance
    """
    path: _path_strs.AbsoluteDirPathStr

    def _special_repr_short(self) -> str:
        return f"Dir[path='{self.path}', file_system_type={self.file_system.special_repr()}]"

    def _special_repr_verbose(self) -> str:
        return f"Dir[path='{self.path}', file_system_type={self.file_system.special_repr()}]"

    def delete(
            self,
            if_non_existent: t.Literal["raise", "return"] = "return",
            recursive: bool = True,
    ) -> None:
        try:
            return self.file_system.delete_dir(
                path=self.path,
                recursive=recursive,
                if_non_existent=if_non_existent
            )
        except Exception as e:
            raise e
        #
        # except _exceptions.FileSystemException as e:
        #     raise e
        # except Exception as e:
        #     raise _exceptions.FileSystemException(
        #         file_system=self.file_system,
        #         extra_info={
        #             "path": self.path,
        #             "error_type": type(e).__name__,
        #             "error_detail": str(e)
        #         }
        #     )

    def iter_dir(self) -> t.Iterator[t.Union[FilePath, DirPath]]:
        for path_i in self.file_system.iter_dir_contents(path=self.path):
            yield self.build_like(path=path_i)

    def iter_dir_contents_files_only(
            self,
            recursive: bool = True
    ) -> list[FilePath]:
        for path_i in self.file_system.iter_dir_contents_files_only(
            path=self.path,
            recursive=recursive
        ):
            yield self.build_like(path=path_i)

    @t.overload
    def joinpath(self, relative_path: _path_strs.RelFilePathStr) -> FilePath:
        ...

    @t.overload
    def joinpath(self, relative_path: _path_strs.RelDirPathStr) -> DirPath:
        ...

    @t.overload
    def joinpath(self, relative_path: str) -> t.Union[FilePath, DirPath]:
        ...

    def joinpath(
            self,
            relative_path: t.Union[str, _path_strs.FileOrDirRelPathT]
    ) -> t.Union[FilePath, DirPath]:
        rel_path_obj = _path_strs.FileOrDirAbsPathTypeAdapter.validate_python(
            relative_path
        )
        new_path_any = self.path.joinpath(rel_path_obj)
        if isinstance(new_path_any, _path_strs.AbsoluteDirPathStr):
            new_path = new_path_any
            return DirPath(
                path=new_path,
                file_system=self.file_system
            )
        elif isinstance(new_path_any, _path_strs.AbsoluteFilePathStr):
            new_path = new_path_any

            return FilePath(
                path=new_path,
                file_system=self.file_system
            )
        else:
            raise ValueError(
                f"'{new_path_any}' is not valid type, type: {type(new_path_any)}"
            )

    def get_name(self) -> str:
        """get simple name, i.e. the most terminal chunk in the path"""
        return self.path.get_name()

    def make_self(
            self,
            if_exists: t.Literal["raise", "return"] = "return",
    ) -> None:
        try:
            self.file_system.make_dir(path=self.path, if_exists=if_exists)
        except Exception as e:
            raise e
        #
        # except _exceptions.FileSystemException as e:
        #     raise e
        # except Exception as e:
        #     raise _exceptions.FileSystemException(
        #         file_system=self.file_system,
        #         extra_info={
        #             "path": self.path,
        #             "error_type": type(e).__name__,
        #             "error_detail": str(e)
        #         }
        #     )

    def download_locally(
            self,
            dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteDirPathStr:
        return self.file_system.download_dir_locally(
            path=self.path,
            dest_dir=dest_dir
        )

    @classmethod
    def init_from_str(cls, raw_str: str) -> DirPath:
        dir_path = _path_strs.AbsoluteDirPathStr(raw_str)
        return DirPath(path=dir_path)


def _str_parser(data: t.Any) -> t.Any:
    if isinstance(data, str):
        path_str = _path_strs.FileOrDirAbsPathTypeAdapter.validate_python(data)
        if isinstance(path_str, _path_strs.AbsoluteFilePathStr):
            return FilePath(path=path_str)
        elif isinstance(path_str, _path_strs.AbsoluteDirPathStr):
            return DirPath(path=path_str)
        else:
            raise ValueError(f"'{path_str}' unexpected type: {type(path_str)}")

    else:
        return data


FileOrDirPathT = t.Annotated[
    _AbstractFileSystemObj.build_dispatched_ann(),
    pydantic.BeforeValidator(_str_parser)
]
"""extends standard dispatched type to support raw strings"""


FileOrDirPathTypeAdapter = pydantic.TypeAdapter(FileOrDirPathT)
"""gives us pydantic parsing logic outside a pydantic class"""