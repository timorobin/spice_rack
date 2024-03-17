from __future__ import annotations
import typing as t
import pydantic

from spice_rack import _bases

if t.TYPE_CHECKING:
    from spice_rack._fs_ops import _path_strs, _file_systems

__all__ = (
    "InvalidPathStrException",
    "NonExistentPathException",
    "PathAlreadyExistsException",
)

ErrorInfoBase = _bases.exceptions.ErrorInfoBase
CustomExceptionBase = _bases.exceptions.CustomExceptionBase


class _InvalidPathStrErrorInfo(ErrorInfoBase):
    """this is raised when one of the path string classes fails to validate a raw string"""
    raw_str: str
    issues: t.List[str]


class InvalidPathStrException(CustomExceptionBase[_InvalidPathStrErrorInfo]):
    """this is raised when one of the path string classes fails to validate a raw string"""
    def __init__(
            self,
            detail: str,
            raw_str: str,
            issues: t.Union[str, list[str]],
            verbose: bool = True,
            extra_info: t.Dict = None
    ):

        issue_lst: t.List[str]
        if isinstance(issues, str):
            issue_lst = [issues]
        else:
            issue_lst = issues

        super().__init__(
            detail=detail,
            error_info={
                "raw_str": raw_str,
                "issues": issue_lst
            },
            verbose=verbose,
            extra_info=extra_info
        )


class _NonExistentPathErrorInfo(ErrorInfoBase):
    """path not found on file system"""
    file_system_info: t.Dict = pydantic.Field(description="the file system we were using")
    path: str


class NonExistentPathException(CustomExceptionBase[_NonExistentPathErrorInfo]):
    def __init__(
            self,
            file_system: _file_systems.AbstractFileSystem,
            path: _path_strs.FileOrDirAbsPathT,
            verbose: bool = True,
            extra_info: t.Dict = None
    ):
        detail = "either the file path does not exist or we do not have access to it"
        error_info = {
            "file_system_info": file_system.__get_logger_data__(),
            "path": file_system.contextualize_abs_path(path)
        }
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info
        )


class _PathAlreadyExistsErrorInfo(ErrorInfoBase):
    """path found when we didn't expect to"""
    file_system_info: t.Dict = pydantic.Field(description="the file system we were using")
    path: str


class PathAlreadyExistsException(CustomExceptionBase[_PathAlreadyExistsErrorInfo]):
    def __init__(
            self,
            file_system: _file_systems.AbstractFileSystem,
            path: _path_strs.FileOrDirAbsPathT,
            verbose: bool = True,
            extra_info: t.Dict = None
    ):
        detail = "this path already exists"
        error_info = {
            "file_system_info": file_system.__get_logger_data__(),
            "path": file_system.contextualize_abs_path(path)
        }
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info
        )
