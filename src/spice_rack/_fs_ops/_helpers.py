from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from spice_rack._fs_ops import _path_strs


__all__ = (
    "get_placeholder_rel_path",
    "is_placeholder_file_path",
)


def get_placeholder_rel_path() -> _path_strs.RelFilePathStr:
    from spice_rack._fs_ops import _path_strs
    return _path_strs.RelFilePathStr(
        "PLACEHOLDER_7b86519eb4ef4ef5b1e16aeb70329fd6.txt"
    )


def is_placeholder_file_path(path: _path_strs.RelOrAbsFilePathT) -> bool:
    placeholder_file_path = get_placeholder_rel_path()
    if str(path).endswith(str(placeholder_file_path)):
        return True
    else:
        return False
