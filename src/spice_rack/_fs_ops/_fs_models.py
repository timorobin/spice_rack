from __future__ import annotations

import os
from abc import abstractmethod
from devtools import pformat
import typing as t
import pydantic

from spice_rack import _bases, _logging
from spice_rack._fs_ops import (
    _path_strs,
    # _exceptions,
    _file_systems,
    _open_modes,
    _file_info
)

__all__ = (
    "FilePath", "DirPath",
    "FileOrDirPathT", "FileOrDirPathTypeAdapter",
    "DeferredFilePath", "DeferredDirPath",
    "FileOrDirDeferredPathT", "FileOrDirDeferredPathTypeAdapter"
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
    def _handle_str(cls, data: t.Any) -> t.Any:
        if isinstance(data, str):
            data = cls.init_from_str(data).model_dump()

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
                self.path,
                if_non_existent=if_non_existent
            )
        except Exception as e:
            raise e

    def open(
            self,
            mode: _open_modes.SupportedOpenModesT = "rb"
    ) -> _open_modes.OpenFileT:
        try:
            return self.file_system.open_file(
                self.path,
                mode=mode
            )
        except Exception as e:
            raise e

    def write(self, data: t.Union[str, bytes], mode: t.Literal["wb", "ab"] = "wb") -> None:
        """
        convenience method to write bytes or str data to a file
        """
        byte_data: bytes
        if isinstance(data, bytes):
            byte_data = data
        else:
            byte_data = data.encode()

        with self.open(mode) as f:
            f.write(byte_data)

    def read_as_str(self, encoding: str = "utf-8") -> str:
        """convenience method to read str data from a file"""
        with self.open("rb") as f:
            byte_data = f.read()
        return byte_data.decode(encoding)

    def get_name(self, include_suffixes: bool = False) -> str:
        """get the name of the file, optionally stripping the name of the suffixes"""
        return self.path.get_name(include_suffixes=include_suffixes)

    def download_locally(
            self,
            dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteFilePathStr:
        """download the file to the local dir specified"""
        return self.file_system.download_file_locally(
            self.path,
            dest_dir
        )

    def ensure_correct_file_ext(self, choices: list[str]) -> None:
        """
        ensure the file path has one of the specified extensions
        Args:
            choices: the valid extensions

        Returns: Nothing

        Raises:
            FilePathInvalidException: if the file path has no extension of it isn't
                one of the choices
        """
        choices = [
            _file_info.FileExt(choice) for choice in choices
        ]
        self.file_system.ensure_correct_file_ext(self.path, choices=choices)

    def ensure_correct_mime_type(self, choices: t.List[_file_info.MimeType]) -> None:
        """
        ensure the file path is one of the specified mime types
        Args:
            choices: the valid mime types

        Returns: Nothing

        Raises:
            InvalidFileMimeTypeException: if we cannot determine the mime type, or it is not one
                of the specified choices
        """
        return self.file_system.ensure_correct_mime_type(
            self.path,
            choices
        )

    def get_file_ext(self) -> t.Optional[_file_info.FileExt]:
        """get the file extension from the file path if there is one"""
        return self.path.get_file_ext()

    def get_mime_type(self) -> t.Optional[_file_info.MimeType]:
        """get the mime type of the file from its file extension, if we have it"""
        return self.path.get_mime_type()

    @classmethod
    def init_from_str(cls, raw_str: str) -> FilePath:
        """
        parse a string into a FilePath instance, inferring the file system from the
        prefix of the string path.

        If the str starts with a '$' we will parse it as a DeferredFilePath instance and
        evaluate it right way into a FilePath inst.
        """
        if raw_str.startswith("$"):
            return DeferredFilePath.model_validate(raw_str).evaluate()
        else:
            inferred_fs = _file_systems.infer_file_system(raw_str)
            path_str = inferred_fs.clean_raw_path_str(raw_str)
            file_path = _path_strs.AbsoluteFilePathStr(path_str)
            return FilePath(path=file_path, file_system=inferred_fs)


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
        """
        delete the directory. recursively deleting all contents if recursive is true.
        """
        return self.file_system.delete_dir(
            self.path,
            recursive=recursive,
            if_non_existent=if_non_existent
        )

    def iter_dir(self) -> t.Iterator[t.Union[FilePath, DirPath]]:
        for path_i in self.file_system.iter_dir_contents(path=self.path):
            yield self.build_like(path_i)

    def iter_dir_contents_files_only(
            self,
            recursive: bool = True
    ) -> list[FilePath]:
        for path_i in self.file_system.iter_dir_contents_files_only(
            self.path,
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
        """get a new FilePath or DirPath by combining this DirPath instance with a provided
        relative path.
        """
        rel_path_obj = _path_strs.FileOrDirRelPathTypeAdapter.validate_python(
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
        """equivalent of mkdir"""
        self.file_system.make_dir(self.path, if_exists=if_exists)

    def download_locally(
            self,
            dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteDirPathStr:
        return self.file_system.download_dir_locally(
            self.path,
            dest_dir
        )

    @classmethod
    def init_from_str(cls, raw_str: str) -> DirPath:
        if raw_str.startswith("$"):
            return DeferredDirPath.model_validate(raw_str).evaluate()
        else:
            inferred_fs = _file_systems.infer_file_system(raw_str)
            path_str = inferred_fs.clean_raw_path_str(raw_str)
            dir_path = _path_strs.AbsoluteDirPathStr(path_str)
            return DirPath(path=dir_path, file_system=inferred_fs)


def _str_parser(data: t.Any) -> t.Any:
    if isinstance(data, str):
        if data.endswith("/"):
            return DirPath.init_from_str(data)
        else:
            return FilePath.init_from_str(data)
    else:
        return data


FileOrDirPathT = t.Annotated[
    _AbstractFileSystemObj.build_dispatched_ann(),
    pydantic.BeforeValidator(_str_parser)
]
"""extends standard dispatched type to support raw strings"""


FileOrDirPathTypeAdapter = pydantic.TypeAdapter(FileOrDirPathT)
"""gives us pydantic parsing logic outside a pydantic class"""


class _DeferredPath(_bases.DispatchableValueModelBase):
    env_var_key: str

    def _get_env_var_val(self) -> DirPath:
        env_val_maybe = os.environ.get(self.env_var_key)
        if env_val_maybe is None:
            raise ValueError(
                f"'{self.env_var_key}' not found in the environment"
            )
        return DirPath.model_validate(env_val_maybe)

    @abstractmethod
    def evaluate(self) -> _AbstractFileSystemObj:
        ...


class DeferredFilePath(_DeferredPath):
    """
    a file path, where part of the path is contained in an environment variable, that is
    looked up when we call 'evaluate' method to convert this instance to a FilePath instance.
    """
    rel_path: _path_strs.RelFilePathStr

    @pydantic.model_validator(mode="before")
    def _handle_str(cls, data: t.Any) -> t.Any:
        if isinstance(data, str):
            if "/" not in data:
                raise ValueError(
                    f"'{data}' cannot be parsed as "
                    f"'{cls.get_class_id()}' bc it has not relative file path beyond"
                    f"the deferred environment key"
                )

            split = data.split("/")
            env_var_key = split[0].replace("$", "")
            rel_path = "/".join(split[1:])

            data = {"env_var_key": env_var_key, "rel_path": rel_path}
        return data

    def evaluate(self) -> FilePath:
        env_val = self._get_env_var_val()
        return env_val.joinpath(self.rel_path)


class DeferredDirPath(_DeferredPath):
    """
    a dir path, where part or all of the path is contained in an environment variable, that is
    looked up when we call 'evaluate' method to convert this instance to a DirPath instance.
    """
    rel_path: t.Optional[_path_strs.RelDirPathStr]

    @pydantic.model_validator(mode="before")
    def _handle_str(cls, data: t.Any) -> t.Any:
        if isinstance(data, str):
            split = data.split("/")
            env_var_key = split[0].replace("$", "")
            rel_path = "/".join(split[1:])
            if not rel_path or rel_path == "/":
                rel_path = None
            data = {"env_var_key": env_var_key, "rel_path": rel_path}
        return data

    def evaluate(self) -> DirPath:
        env_val = self._get_env_var_val()
        if self.rel_path:
            return env_val.joinpath(self.rel_path)
        else:
            return env_val


def _deferred_str_parser(data: t.Any) -> t.Any:
    if isinstance(data, str):
        if data.startswith("$"):
            if data.endswith("/"):
                return DeferredDirPath.model_validate(data)
            else:
                return DeferredFilePath.model_validate(data)
        else:
            raise ValueError(
                f"a deferred path str must start with '$', '{data}' does not"
            )
    else:
        return data


FileOrDirDeferredPathT = t.Annotated[
    t.Union[DeferredFilePath, DeferredDirPath],
    pydantic.BeforeValidator(_deferred_str_parser)
]
"""extends standard dispatched type to support raw strings"""


FileOrDirDeferredPathTypeAdapter: pydantic.TypeAdapter[FileOrDirDeferredPathT] = (
    pydantic.TypeAdapter(FileOrDirDeferredPathT)
)
"""gives us pydantic parsing logic outside a pydantic class"""
