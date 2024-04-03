from __future__ import annotations
import typing as t
import pydantic

from spice_rack._fs_ops._fs_models import (
    _base,
    _file,
    _dir,
    _deferred
)


__all__ = (
    "FileOrDirPathT", "FileOrDirPathTypeAdapter",
    "FileOrDirDeferredPathT", "FileOrDirDeferredPathTypeAdapter"
)


def _str_parser(data: t.Any) -> t.Any:
    if isinstance(data, str):
        if data.endswith("/"):
            return _dir.DirPath.init_from_str(data)
        else:
            return _file.FilePath.init_from_str(data)

    else:
        return data


FileOrDirPathT = t.Annotated[
    _base.AbstractFileSystemObj.build_dispatched_ann(),
    pydantic.BeforeValidator(_str_parser)
]
"""extends standard dispatched type to support raw strings"""


FileOrDirPathTypeAdapter = pydantic.TypeAdapter(FileOrDirPathT)
"""gives us pydantic parsing logic outside a pydantic class"""


def _deferred_str_parser(data: t.Any) -> t.Any:
    if isinstance(data, str):
        if data.startswith("$"):
            if data.endswith("/"):
                return _deferred.DeferredDirPath.model_validate(data)
            else:
                return _deferred.DeferredFilePath.model_validate(data)
        else:
            raise ValueError(
                f"a deferred path str must start with '$', '{data}' does not"
            )
    else:
        return data


FileOrDirDeferredPathT = t.Annotated[
    t.Union[_deferred.DeferredFilePath, _deferred.DeferredDirPath],
    pydantic.BeforeValidator(_deferred_str_parser)
]
"""extends standard dispatched type to support raw strings"""


FileOrDirDeferredPathTypeAdapter: pydantic.TypeAdapter[FileOrDirDeferredPathT] = (
    pydantic.TypeAdapter(FileOrDirDeferredPathT)
)
"""gives us pydantic parsing logic outside a pydantic class"""
