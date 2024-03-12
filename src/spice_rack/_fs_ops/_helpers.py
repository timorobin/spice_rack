from __future__ import annotations
import typing as t

from pathlib import Path

if t.TYPE_CHECKING:
    from spice_rack._fs_ops import _path_strs


__all__ = (
    "is_dir_like",
    "get_placeholder_rel_path",
    "is_placeholder_file_path"
)


def is_dir_like(raw_str: str, strict: bool = False) -> bool:
    if raw_str.endswith("/"):
        return True

    if strict:
        return False
    else:
        if Path(raw_str).suffix:
            return False
        else:
            return True


def get_placeholder_rel_path() -> _path_strs.RelFilePathStr:
    from spice_rack._fs_ops import _path_strs
    return _path_strs.RelFilePathStr(
        "PLACEHOLDER_7b86519eb4ef4ef5b1e16aeb70329fd6.txt"
    )


def is_placeholder_file_path(path: _path_strs.RelOrAbsFilePathT) -> bool:
    from spice_rack._fs_ops import _path_strs

    placeholder_file_path = get_placeholder_rel_path()
    if str(path).endswith(str(placeholder_file_path)):
        return True
    else:
        return False
