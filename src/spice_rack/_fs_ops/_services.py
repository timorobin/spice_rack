from __future__ import annotations
import typing as t
import json
import yaml
import pydantic

from spice_rack._fs_ops import _fs_models


__all__ = (
    "read_json",
    "write_json",
    "read_yaml",
    "write_yaml"
)


@pydantic.validate_call
def read_json(__file_path: _fs_models.FilePath) -> t.Dict[str, pydantic.JsonValue]:
    __file_path.ensure_exists()
    __file_path.ensure_correct_file_ext(choices=["json"])
    with __file_path.open("rb") as f:
        data = json.load(f)
    return data


@pydantic.validate_call
def write_json(
        __file_path: _fs_models.FilePath,
        __data: t.Dict[str, pydantic.JsonValue],
        if_exists: t.Literal["raise", "overwrite"] = "overwrite"
) -> None:
    if if_exists == "raise":
        __file_path.ensure_nonexistent()

    __file_path.ensure_correct_file_ext(choices=["json"])
    with __file_path.open("wb") as f:
        json.dump(__data, f)
    return


@pydantic.validate_call
def read_yaml(__file_path: _fs_models.FilePath) -> t.Dict[str, t.Any]:
    __file_path.ensure_exists()
    __file_path.ensure_correct_file_ext(choices=["yaml", "yml"])
    with __file_path.open("rb") as f:
        data = yaml.unsafe_load(f)
    return data


@pydantic.validate_call
def write_yaml(
        __file_path: _fs_models.FilePath,
        __data: t.Dict[str, pydantic.JsonValue],
        if_exists: t.Literal["raise", "overwrite"] = "overwrite"
) -> None:
    if if_exists == "raise":
        __file_path.ensure_nonexistent()

    __file_path.ensure_correct_file_ext(choices=["yaml", "yml"])
    with __file_path.open("wb") as f:
        yaml.dump(__data, f)
    return
