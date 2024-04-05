from __future__ import annotations
import typing as t
import pydantic

from spice_rack._fs_ops import _path_strs, _file_systems
from spice_rack._fs_ops._fs_models._base import AbstractFileSystemObj

if t.TYPE_CHECKING:
    from spice_rack._fs_ops._fs_models._file import FilePath


__all__ = (
    "DirPath",
)


class DirPath(AbstractFileSystemObj):
    """
    this class represents a directory on a file system,
    with the absolute full path string, and the file system instance
    """
    path: _path_strs.AbsoluteDirPathStr = pydantic.Field(
        description="the path string on the underlying file system. Must be absolute. You can use the "
                    "file system-specific format, e.g. 'gs://bucket/dir/' and we will convert it to "
                    "/bucket/dir/' and make sure the file_system aligns"
    )

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
            from spice_rack._fs_ops._fs_models._file import FilePath

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
            from spice_rack._fs_ops._fs_models._deferred import DeferredDirPath
            return DeferredDirPath.model_validate(raw_str).evaluate()
        else:
            inferred_fs = _file_systems.infer_file_system(raw_str)
            path_str = inferred_fs.clean_raw_path_str(raw_str)
            dir_path = _path_strs.AbsoluteDirPathStr(path_str)
            return DirPath(path=dir_path, file_system=inferred_fs)
