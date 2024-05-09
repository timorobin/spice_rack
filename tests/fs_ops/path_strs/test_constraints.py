import pytest
import pydantic
import typing as t

from spice_rack import fs_ops


def test_file_ext_constraint_schema_gen():
    type_adapter = pydantic.TypeAdapter(
        t.Annotated[fs_ops.path_strs.RelFilePathStr, fs_ops.FileExtConstraint("txt")]
    )
    assert type_adapter.core_schema["metadata"]["valid_file_extensions"] == ["txt"]


def test_file_ext_constraint_on_path_str():

    class SomeModel(pydantic.BaseModel):
        text_path: t.Annotated[fs_ops.path_strs.RelFilePathStr, fs_ops.FileExtConstraint("txt")]

    with pytest.raises(pydantic.ValidationError):
        SomeModel(text_path="file.json")

    assert SomeModel(text_path="file.txt")
