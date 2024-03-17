from __future__ import annotations
import typing as t
from pathlib import Path


__all__ = (
    "file_validator",
    "dir_validator",
    "rel_validator",
    "abs_validator"
)


def file_validator(
        raw_str: str
) -> t.List[str]:
    """checks path makes sense as a relative or absolute file"""
    if raw_str.endswith("/"):
        return ["a file path str cannot end in '/'"]
    else:
        return []


def dir_validator(raw_str: str, strict: bool = False) -> t.List[str]:
    if raw_str.endswith("/"):
        return []

    issue: t.Optional[str] = None
    if Path(raw_str).suffix:
        issue = "this path has a file extension suffix, so it cannot be a directory path"
    else:
        if strict:
            issue = "a dir path must end in '/'"

    if issue is not None:
        return [issue]
    else:
        return []


def rel_validator(raw_str: str) -> t.List[str]:
    if raw_str.startswith("/"):
        return [
            "a relative path cannot start with '/'"
        ]
    else:
        return []


def abs_validator(raw_str: str) -> t.List[str]:
    if not raw_str.startswith("/"):
        return [
            "an absolute path must start with '/'"
        ]
    else:
        return []
