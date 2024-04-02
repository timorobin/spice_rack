from __future__ import annotations
import typing as t
import pydantic

from spice_rack import _bases

if t.TYPE_CHECKING:
    from spice_rack._fs_ops import _path_strs, _file_systems, _file_info

__all__ = (
    "InvalidPathStrException",
    "NonExistentPathException",
    "PathAlreadyExistsException",
    "InvalidFileExtensionException",
    "InvalidFileMimeTypeException"
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


class _InvalidFileExtensionErrorInfo(ErrorInfoBase):
    full_path: str
    file_ext_found: t.Optional[str]
    file_ext_choices: t.List[str]


class InvalidFileExtensionException(CustomExceptionBase[_InvalidFileExtensionErrorInfo]):
    def __init__(
            self,
            path: _path_strs.FileOrDirAbsPathT,
            file_ext_found: t.Optional[_file_info.FileExt],
            file_ext_choices: t.List[_file_info.FileExt],
            verbose: bool = True,
            extra_info: t.Dict = None,
    ):
        error_info = {
            "full_path": path,
            "file_ext_found": file_ext_found,
            "file_ext_choices": file_ext_choices,
        }
        if not file_ext_found:
            detail = (f"the path, '{path}' had no file extension, "
                      f"but one the specified file extensions was expected")
        else:
            detail = (f"the path, '{path}' had file extension, '{file_ext_found}' "
                      f"which is not one of the specified file extensions")
        super().__init__(
            detail=detail,
            error_info=error_info,
            extra_info=extra_info,
            verbose=verbose
        )


class _InvalidFileMimeTypeErrorInfo(ErrorInfoBase):
    full_path: str
    mime_type_found: t.Optional[str]
    mime_type_choices: t.List[str]


class InvalidFileMimeTypeException(CustomExceptionBase[_InvalidFileMimeTypeErrorInfo]):
    def __init__(
            self,
            path: _path_strs.FileOrDirAbsPathT,
            mime_type_found: t.Optional[str],
            mime_type_choices: t.List[str],
            verbose: bool = True,
            extra_info: t.Dict = None,
    ):
        error_info = {
            "full_path": path,
            "mime_type_found": mime_type_found,
            "mime_type_choices": mime_type_choices,
        }
        if not mime_type_found:
            detail = (f"the path, '{path}' had no mime type, "
                      f"but one the specified mime types was expected")
        else:
            detail = (f"the path, '{path}' had mime type, '{mime_type_found}' "
                      f"which is not one of the specified mime types")
        super().__init__(
            detail=detail,
            error_info=error_info,
            extra_info=extra_info,
            verbose=verbose
        )
