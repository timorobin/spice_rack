from __future__ import annotations
from abc import abstractmethod
import typing as t
from fsspec.spec import AbstractFileSystem as AbstractFsSpecFileSystem

from spice_rack import _bases
from spice_rack._fs_ops import _path_strs, _helpers, _file_ext, _open_modes


__all__ = (
    "AbstractFileSystem",
)


class AbstractFileSystem(_bases.dispatchable.DispatchableValueModelBase):
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

    def clean_raw_path_str(
            self,
            raw_path: str,
    ) -> _path_strs.FileOrDirAbsPathT:
        assert isinstance(raw_path, str), type(raw_path)
        cleaned_path = raw_path.replace(
            self.get_fs_specific_prefix(),
            "/",
            1
        )
        if _helpers.is_dir_like(raw_str=cleaned_path):
            return _path_strs.AbsoluteDirPathStr(cleaned_path)
        else:
            return _path_strs.AbsoluteFilePathStr(cleaned_path)

    def contextualize_abs_path(self, path: _path_strs.FileOrDirAbsPathT) -> str:
        """
        take an absolute path, in the general representation
        and add the file system specific prefix
        """
        if not isinstance(path, (_path_strs.AbsoluteFilePathStr, _path_strs.AbsoluteDirPathStr)):
            raise ValueError(f"should be an absolute path type, encountered type: {type(path)}")
        prefix_val = self.get_fs_specific_prefix()
        formatted_path_str = prefix_val + str(path)[1:]
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
        return self.get_file_system_type().value

    @t.final
    def exists(self, path: _path_strs.FileOrDirAbsPathT) -> bool:
        """
        returns True if this file system object exists, false otherwise
        """

        # todo: what if perms issue not existence issue?
        return self.fsspec_obj.exists(self.contextualize_abs_path(path))

    def ensure_exists(self, path: _path_strs.FileOrDirAbsPathT) -> None:
        """
        ensure the file or dir path exists, raising an exception if not

        Args:
            path: the path to the file or directory

        Returns: Nothing

        Raises:
            NonExistentPathException: if the path doesn't exist, or we cannot access it

        """
        exists = self.exists(path)
        if not exists:
            raise ValueError(
                f"'{self.contextualize_abs_path(path)}' "
                f"either doesn't exist or we don't have access to it"
            )
            # raise _exceptions.NonExistentPathException(
            #     file_system=self,
            #     path=path,
            #     extra_info={}
            # )
        else:
            return

    @staticmethod
    def ensure_correct_file_ext(
            path: _path_strs.RelOrAbsFilePathT,
            choices: list[_file_ext.FileExt]
    ) -> None:
        """
        ensure the file path has one of the specified extensions
        Args:
            path: the path we are checking
            choices: the valid extensions

        Returns: Nothing

        Raises:
            FilePathInvalidException: if the file path has no extension of it isn't
                one of the choices

        """
        file_ext = path.get_file_ext()
        if file_ext is None:
            raise ValueError(
                f"'{path}' has no file extensions"
            )
            # raise _exceptions.FilePathInvalidException(
            #     file_system=self,
            #     path=path,
            #     reason="no file extension found on the file path",
            #     extra_info={
            #         "choices": choices,
            #     }
            # )

        if file_ext not in choices:
            raise ValueError(
                f"'{path}' file extension isn't one of {choices}"
            )
            # raise _exceptions.FilePathInvalidException(
            #     file_system=self,
            #     path=path,
            #     reason=f"the file extension, '{file_ext}', not one of the choices",
            #     extra_info={
            #         "file_path": path,
            #         "choices": choices,
            #     }
            # )
        return

    # def ensure_correct_mime_type(
    #         self,
    #         path: _path_strs.AbsoluteFilePathStr,
    #         choices: list[_special_types.MimeType]
    # ) -> None:
    #     """
    #     ensure the file path is one of the specified mime types
    #     Args:
    #         path: the path we are checking
    #         choices: the valid mime types
    #
    #     Returns: Nothing
    #
    #     Raises:
    #         FilePathInvalidException: if we cannot determine the mime type, or it is not one
    #             of the specified choices
    #     """
    #     mime_type = path.get_file_ext()
    #     if mime_type is None:
    #         raise _exceptions.FilePathInvalidException(
    #             file_system=self,
    #             path=path,
    #             reason="unable to infer mime type from the file path",
    #             extra_info={
    #                 "choices": choices,
    #             }
    #         )
    #     if mime_type not in choices:
    #         raise _exceptions.FilePathInvalidException(
    #             file_system=self,
    #             path=path,
    #             reason=f"the inferred mime type, '{mime_type}', not one of the choices",
    #             extra_info={
    #                 "choices": choices,
    #             }
    #         )
    #     return

    def open_file(
            self,
            path: _path_strs.AbsoluteFilePathStr,
            mode: _open_modes.SupportedOpenModesT
    ) -> _open_modes.OpenFileT:
        """
        return a readable open file object. todo: revisit type annotations of the return type here

        Args:
            path: the file path str
            mode: the mode we are opening in

        Returns:
            the readable open file object
        """
        if mode != "wb":
            self.ensure_exists(path=path)
        return self.fsspec_obj.open(path=self.contextualize_abs_path(path), mode=mode)

    def delete_file(
            self,
            path: _path_strs.AbsoluteFilePathStr,
            if_non_existent: t.Literal["raise", "return"] = "return"
    ) -> None:
        """
        delete the file
        """

        exists = self.exists(path)
        if not exists:
            if if_non_existent == "raise":
                self.ensure_exists(path)

        else:
            # what if perms issue not existence issue?
            self.fsspec_obj.delete(path=self.contextualize_abs_path(path), recursive=True)
        return

    def delete_dir(
            self,
            path: _path_strs.AbsoluteDirPathStr,
            recursive: bool = True,
            if_non_existent: t.Literal["raise", "return"] = "return"
    ) -> None:
        """
        delete the directory
        """

        from devtools import debug
        debug(path)

        exists = self.exists(path)

        debug(path)

        if not exists:
            if if_non_existent == "raise":
                self.ensure_exists(path)

        else:
            # what if perms issue not existence issue?
            self.fsspec_obj.delete(path=self.contextualize_abs_path(path), recursive=recursive)
        return

    def iter_dir_contents(
            self,
            path: _path_strs.AbsoluteDirPathStr,
    ) -> t.Iterator[_path_strs.FileOrDirAbsPathT]:
        """iterate over the top level dir contents"""
        for raw_info_rec_i in self.fsspec_obj.listdir(
            self.contextualize_abs_path(path)
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

    def list_dir_contents(
            self,
            path: _path_strs.AbsoluteDirPathStr
    ) -> list[_path_strs.FileOrDirAbsPathT]:
        return list(self.iter_dir_contents(path=path))

    def iter_dir_contents_files_only(
            self,
            path: _path_strs.AbsoluteDirPathStr,
            recursive: bool = True
    ) -> t.Iterator[_path_strs.AbsoluteFilePathStr]:
        for path_i in self.iter_dir_contents(path=path):
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

    def make_dir(
            self,
            path: _path_strs.AbsoluteDirPathStr,
            if_exists: t.Literal["raise", "return"] = "return",
            create_parents: bool = True
    ) -> None:
        if self.exists(path=path):
            if if_exists == "raise":
                raise ValueError(
                    f"'{path}'already exists, cannot make it."
                )
                # raise _exceptions.PathAlreadyExistsException(
                #     file_system=self,
                #     path=path,
                #     extra_info={
                #         "action_attempted": "make_dir"
                #     }
                # )
            else:
                return

        else:
            self.fsspec_obj.mkdir(
                path=self.contextualize_abs_path(path),
                create_parents=create_parents
            )

    def write_text(
            self,
            data: str,
            path: _path_strs.AbsoluteFilePathStr,
            if_exists: t.Literal["raise", "overwrite"]
    ) -> None:
        if self.exists(path):
            if if_exists == "raise":
                raise ValueError(f"'{self.contextualize_abs_path(path)}' exists already")
            else:
                self.delete_file(path)

        self.ensure_exists(path)
        with self.open_file(path, mode="wb") as f:
            f.write(data)
        return

    def read_text(self, path: _path_strs.AbsoluteFilePathStr) -> str:
        self.ensure_exists(path)
        with self.open_file(path, mode="rb") as f:
            data = f.read()
        return data.decode()

    # def download_file_locally(
    #         self,
    #         path: _path_strs.AbsoluteFilePathStr,
    #         dest_dir: _path_strs.AbsoluteDirPathStr
    # ) -> _path_strs.AbsoluteFilePathStr:
    #     from fs_ops._file_systems import LocalFileSystem
    #     local_fs = LocalFileSystem()
    #     local_fs.make_dir(dest_dir, if_exists="return", create_parents=True)
    #
    #     local_path = dest_dir.joinpath(
    #         _path_strs.RelFilePathStr(path.get_name(include_suffixes=True))
    #     )
    #     self.fsspec_obj.download(
    #         lpath=local_fs.contextualize_abs_path(local_path),
    #         rpath=self.contextualize_abs_path(path)
    #     )
    #     return local_path
    #
    # def download_dir_locally(
    #         self,
    #         path: _path_strs.AbsoluteDirPathStr,
    #         dest_dir: _path_strs.AbsoluteDirPathStr
    # ) -> _path_strs.AbsoluteDirPathStr:
    #     from fs_ops._file_systems import LocalFileSystem
    #
    #     local_fs = LocalFileSystem()
    #     local_fs.make_dir(dest_dir, if_exists="return", create_parents=True)
    #
    #     local_path = dest_dir.joinpath(
    #         _path_strs.RelDirPathStr(path.get_name())
    #     )
    #     self.fsspec_obj.download(
    #         lpath=local_fs.contextualize_abs_path(local_path),
    #         rpath=self.contextualize_abs_path(path),
    #         recursive=True
    #     )
    #
    #     for local_path_i in local_fs.iter_dir_contents_files_only(local_path):
    #         if _helpers.is_placeholder_file_path(local_path_i):
    #             local_fs.delete_file(
    #                 local_path_i, if_non_existent="return"
    #             )
    #     return local_path
