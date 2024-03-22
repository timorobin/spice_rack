from __future__ import annotations


__all__ = (
    "get_current_datetime_for_file_path",
)


def get_current_datetime_for_file_path() -> str:
    from spice_rack._ts_service._timestamp import Timestamp
    return Timestamp.now().to_file_path_fmat()
