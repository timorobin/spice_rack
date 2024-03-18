from __future__ import annotations
from typing import final
from pathlib import Path
from fsspec.implementations.local import LocalFileSystem as FsSpecLocalFileSystem

from spice_rack._fs_ops._file_systems import _base
from spice_rack._fs_ops import _path_strs


__all__ = (
    "LocalFileSystem",
)


@final
class LocalFileSystem(_base.AbstractFileSystem, class_id="local"):
    """file system implementation for the local file system"""

    def build_fsspec_file_system(self) -> FsSpecLocalFileSystem:
        return FsSpecLocalFileSystem()

    @classmethod
    def get_fs_specific_prefix(cls) -> str:
        return "/"

    def get_home_dir(self) -> _path_strs.AbsoluteDirPathStr:
        return _path_strs.AbsoluteDirPathStr(str(Path().home()))
