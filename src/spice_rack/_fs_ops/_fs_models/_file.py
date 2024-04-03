from __future__ import annotations
import typing as t

from spice_rack._fs_ops import (
    _path_strs,
    # _exceptions,
    _file_systems,
    _open_modes,
    _file_info
)

from spice_rack._fs_ops._fs_models._base import AbstractFileSystemObj

if t.TYPE_CHECKING:
    from spice_rack._fs_ops._fs_models._deferred import DeferredFilePath


__all__ = (
    "FilePath",
)


class FilePath(AbstractFileSystemObj):
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
            from spice_rack._fs_ops._fs_models._deferred import DeferredFilePath
            return DeferredFilePath.model_validate(raw_str).evaluate()
        else:
            inferred_fs = _file_systems.infer_file_system(raw_str)
            path_str = inferred_fs.clean_raw_path_str(raw_str)
            file_path = _path_strs.AbsoluteFilePathStr(path_str)
            return FilePath(path=file_path, file_system=inferred_fs)
