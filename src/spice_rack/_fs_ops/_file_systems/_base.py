from __future__ import annotations
from abc import abstractmethod
import typing as t
from fsspec.spec import AbstractFileSystem as AbstractFsSpecFileSystem
import pydantic

from spice_rack import _bases, _logging
from spice_rack._fs_ops import _path_strs, _file_info, _open_modes, _exceptions


__all__ = (
    "AbstractFileSystem",
)


class AbstractFileSystem(
    _bases.dispatchable.DispatchableValueModelBase,
    _logging.log_extra.LoggableObjMixin
):
    """base class for all fsspec file system wrappers"""

    @abstractmethod
    def build_fsspec_file_system(self) -> AbstractFsSpecFileSystem:
        ...

    @property
    def fsspec_obj(self) -> AbstractFsSpecFileSystem:
        return self.build_fsspec_file_system()

    @classmethod
    @abstractmethod
    def get_fs_specific_prefix(cls) -> str:
        ...

    @classmethod
    @pydantic.validate_call
    def clean_raw_path_str(
            cls,
            __raw_path: str,
    ) -> _path_strs.FileOrDirAbsPathT:
        """
        strip the raw path of the file system-specific prefix, and cast it to a
        standardized directory or file path representation.

        This is the inverse of 'contextualize_abs_path'.
        """
        cleaned_path = __raw_path.replace(
            cls.get_fs_specific_prefix(),
            "/",
            1
        )
        return _path_strs.FileOrDirAbsPathTypeAdapter.validate_python(
            cleaned_path
        )

    @pydantic.validate_call
    def contextualize_abs_path(self, __path: _path_strs.FileOrDirAbsPathT) -> str:
        """
        convert a standardized file or directory path representation into a
        str starting with the file system-specific prefix.
        This is the inverse of 'clean_raw_path_str'.
        """
        prefix_val = self.get_fs_specific_prefix()
        formatted_path_str = prefix_val + str(__path)[1:]
        return formatted_path_str

    @abstractmethod
    def get_home_dir(self) -> _path_strs.AbsoluteDirPathStr:
        ...

    def __hash__(self) -> int:
        return hash(
            self.contextualize_abs_path(self.get_home_dir())
        )

    def __eq__(self, other: AbstractFileSystem) -> bool:
        if type(self) == type(other):  # noqa
            if hash(self) == hash(other):
                return True
        return False

    def special_repr(self) -> str:
        return f"FileSystem[{self.class_id}]"

    def __get_logger_data__(self) -> t.Dict:
        return {
            "file_system_type": self.class_id,
            "file_system_home_dir": self.contextualize_abs_path(self.get_home_dir())
        }

    @pydantic.validate_call
    def exists(self, __path: _path_strs.FileOrDirAbsPathT) -> bool:
        """
        returns True if this file system object exists, false otherwise
        """

        # todo: what if perms issue not existence issue?
        return self.fsspec_obj.exists(self.contextualize_abs_path(__path))

    @pydantic.validate_call
    def ensure_exists(self, __path: _path_strs.FileOrDirAbsPathT) -> None:
        """
        ensure the file or dir path exists, raising an exception if not

        Args:
            __path: the path to the file or directory

        Returns: Nothing

        Raises:
            NonExistentPathException: if the path doesn't exist, or we cannot access it

        """
        exists = self.exists(__path)
        if not exists:
            raise _exceptions.NonExistentPathException(
                file_system=self,
                path=__path,
            )
        else:
            return

    @pydantic.validate_call
    def ensure_nonexistent(self, __path: _path_strs.FileOrDirAbsPathT) -> None:
        """
        ensure the file or dir path does exist, raising an exception if it does

        Args:
            __path: the path to the file or directory

        Returns: Nothing

        Raises:
            PathAlreadyExistsException: if the path does exist
        """
        exists = self.exists(__path)
        if exists:
            raise _exceptions.PathAlreadyExistsException(
                file_system=self,
                path=__path,
            )
        else:
            return

    @pydantic.validate_call
    def ensure_correct_file_ext(
            self,
            __path: _path_strs.RelOrAbsFilePathT,
            *,
            choices: list[_file_info.FileExt]
    ) -> None:
        """
        ensure the file path has one of the specified extensions
        Args:
            __path: the path we are checking
            choices: the valid extensions

        Returns: Nothing

        Raises:
            FilePathInvalidException: if the file path has no extension of it isn't
                one of the choices
        """
        file_ext = __path.get_file_ext()
        if file_ext is None or file_ext not in choices:
            raise _exceptions.InvalidFileExtensionException(
                path=__path,
                file_ext_found=file_ext,
                file_ext_choices=choices,
            )
        return

    @pydantic.validate_call
    def ensure_correct_mime_type(
            self,
            __path: _path_strs.AbsoluteFilePathStr,
            *,
            choices: list[_file_info.MimeType]
    ) -> None:
        """
        ensure the file path is one of the specified mime types
        Args:
            __path: the path we are checking
            choices: the valid mime types

        Returns: Nothing

        Raises:
            InvalidFileMimeTypeException: if we cannot determine the mime type, or it is not one
                of the specified choices
        """
        mime_type_found = __path.get_mime_type()
        if not mime_type_found or mime_type_found not in choices:
            raise _exceptions.InvalidFileMimeTypeException(
                path=__path,
                mime_type_found=mime_type_found,
                mime_type_choices=choices,
                verbose=True
            )

    @pydantic.validate_call
    def open_file(
            self,
            __path: _path_strs.AbsoluteFilePathStr,
            mode: _open_modes.SupportedOpenModesT
    ) -> _open_modes.OpenFileT:
        """
        return a readable open file object. todo: revisit type annotations of the return type here

        Args:
            __path: the file path str
            mode: the mode we are opening in

        Returns:
            the readable open file object
        """
        if mode != "wb":
            self.ensure_exists(__path)
        return self.fsspec_obj.open(
            path=self.contextualize_abs_path(__path), mode=mode
        )

    @pydantic.validate_call
    def delete_file(
            self,
            __path: _path_strs.AbsoluteFilePathStr,
            *,
            if_non_existent: t.Literal["raise", "return"] = "return"
    ) -> None:
        """
        delete the file
        """
        exists = self.exists(__path)
        if not exists:
            if if_non_existent == "raise":
                self.ensure_exists(__path)

        else:
            # what if perms issue not existence issue?
            self.fsspec_obj.delete(path=self.contextualize_abs_path(__path), recursive=True)
        return

    @pydantic.validate_call
    def delete_dir(
            self,
            __path: _path_strs.AbsoluteDirPathStr,
            *,
            recursive: bool = True,
            if_non_existent: t.Literal["raise", "return"] = "return"
    ) -> None:
        """
        delete the directory, if recursive is true, we delete all files and subdirectories
        """
        exists = self.exists(__path)
        if not exists:
            if if_non_existent == "raise":
                self.ensure_exists(__path)

        else:
            # what if perms issue not existence issue?
            self.fsspec_obj.delete(path=self.contextualize_abs_path(__path), recursive=recursive)
        return

    @pydantic.validate_call
    def iter_dir_contents(
            self,
            __path: _path_strs.AbsoluteDirPathStr,
    ) -> t.Iterator[_path_strs.FileOrDirAbsPathT]:
        """iterate over the top level dir contents"""
        for raw_info_rec_i in self.fsspec_obj.listdir(
            self.contextualize_abs_path(__path)
        ):
            raw_path_i = raw_info_rec_i.get("name")
            if raw_path_i is None:
                raise ValueError(
                    "'name' not found in record?"
                )
                # raise _exceptions.FileSystemException(
                #     file_system=self,
                #     extra_info={
                #         "dir_path": path,
                #         "raw_record": raw_info_rec_i,
                #         "issue": "'name' not found in record?"
                #     },
                # )

            path_i: _path_strs.FileOrDirAbsPathT
            raw_type = raw_info_rec_i.get("type")
            formatted_path_i = str(self.clean_raw_path_str(raw_path_i))

            if raw_type == "file":
                path_i = _path_strs.AbsoluteFilePathStr(formatted_path_i)

            elif raw_type == "directory":
                if not formatted_path_i.endswith("/"):
                    formatted_path_i = f"{formatted_path_i}/"
                path_i = _path_strs.AbsoluteDirPathStr(formatted_path_i)

            else:
                raise ValueError(f"unexpected type val: '{raw_type}'")

            yield path_i

    @pydantic.validate_call
    def list_dir_contents(
            self,
            __path: _path_strs.AbsoluteDirPathStr
    ) -> list[_path_strs.FileOrDirAbsPathT]:
        """exhaust the iterator built from 'iter_dir_contents' returning
        the items in a list"""
        return list(self.iter_dir_contents(__path))

    @pydantic.validate_call
    def iter_dir_contents_files_only(
            self,
            __path: _path_strs.AbsoluteDirPathStr,
            *,
            recursive: bool = True
    ) -> t.Iterator[_path_strs.AbsoluteFilePathStr]:
        """iterate over every file in a directory, recursing into subdirectories if
        recursive is True"""
        for path_i in self.iter_dir_contents(__path):
            if isinstance(path_i, _path_strs.AbsoluteFilePathStr):
                yield path_i
            elif isinstance(path_i, _path_strs.AbsoluteDirPathStr):
                if recursive:
                    for path_ij in self.iter_dir_contents_files_only(
                        path=path_i,
                        recursive=recursive,
                    ):
                        yield path_ij
                else:
                    continue
            else:
                raise ValueError(type(path_i))

    @pydantic.validate_call
    def make_dir(
            self,
            __path: _path_strs.AbsoluteDirPathStr,
            *,
            if_exists: t.Literal["raise", "return"] = "return",
            create_parents: bool = True
    ) -> None:
        """create a new directory, and parents if the parent directory doesn't exist"""
        if self.exists(__path):
            if if_exists == "raise":
                raise _exceptions.PathAlreadyExistsException(
                    file_system=self,
                    path=__path,
                    extra_info={
                        "action_attempted": "make_dir"
                    }
                )
            else:
                return

        else:
            self.fsspec_obj.mkdir(
                path=self.contextualize_abs_path(__path),
                create_parents=create_parents
            )

    @pydantic.validate_call
    def download_file_locally(
            self,
            __source_path: _path_strs.AbsoluteFilePathStr,
            __local_dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteFilePathStr:
        """
        download file from current file system into the local file system.

        the downloaded file will have the same name as the source file, inside the
        specified local directory.
        """
        from spice_rack._fs_ops._file_systems import _local
        local_fs = _local.LocalFileSystem()
        local_fs.make_dir(__local_dest_dir, if_exists="return", create_parents=True)

        local_path = __local_dest_dir.joinpath(
            _path_strs.RelFilePathStr(__source_path.get_name(include_suffixes=True))
        )
        self.fsspec_obj.download(
            lpath=local_fs.contextualize_abs_path(local_path),
            rpath=self.contextualize_abs_path(__source_path)
        )
        return local_path

    @pydantic.validate_call
    def download_dir_locally(
            self,
            __source_dir: _path_strs.AbsoluteDirPathStr,
            __local_dest_dir: _path_strs.AbsoluteDirPathStr
    ) -> _path_strs.AbsoluteDirPathStr:
        """
        download directory from current file system into the local file system.

        the downloaded directory will have the same name as the source directory, inside the
        specified local directory.
        """
        from spice_rack._fs_ops._file_systems import _local
        from spice_rack._fs_ops._helpers import is_placeholder_file_path
        local_fs = _local.LocalFileSystem()
        local_fs.make_dir(__local_dest_dir, if_exists="return", create_parents=True)

        local_path = __local_dest_dir.joinpath(
            _path_strs.RelDirPathStr(__source_dir.get_name())
        )
        self.fsspec_obj.download(
            lpath=local_fs.contextualize_abs_path(local_path),
            rpath=self.contextualize_abs_path(__source_dir),
            recursive=True
        )

        # remove possible placeholder files
        for local_path_i in local_fs.iter_dir_contents_files_only(local_path):
            if is_placeholder_file_path(local_path_i):
                local_fs.delete_file(
                    local_path_i, if_non_existent="return"
                )
        return local_path
