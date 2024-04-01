from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from spice_rack._fs_ops import _file_systems


__all__ = (
    "infer_file_system",
)


def infer_file_system(raw_path: str) -> _file_systems.AnyFileSystemT:
    from spice_rack._fs_ops import _file_systems

    # if starts with "gs://" we assume gcp
    if raw_path.startswith("gs://"):
        return _file_systems.GcsFileSystem()

    else:
        # fallback is local
        return _file_systems.LocalFileSystem()
