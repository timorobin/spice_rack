import pytest
from pathlib import Path
import pydantic
import typing as t
import json

from spice_rack import fs_ops


def test_file_ext_constraint_schema_gen():
    type_adapter = pydantic.TypeAdapter(
        t.Annotated[fs_ops.FilePath, fs_ops.FileExtConstraint("txt")]
    )
    assert type_adapter.core_schema["metadata"]["valid_file_extensions"] == ["txt"]


@pytest.fixture(scope="module")
def file_system() -> fs_ops.file_systems.LocalFileSystem:
    return fs_ops.file_systems.LocalFileSystem()


# also tests make dir

@pytest.fixture(scope="module")
def work_dir(file_system) -> fs_ops.path_strs.AbsoluteDirPathStr:
    p = Path(__file__).parent.joinpath("test_dir/")
    dir_path = fs_ops.path_strs.AbsoluteDirPathStr(str(p))
    file_system.make_dir(dir_path, if_exists="raise")
    yield dir_path
    file_system.delete_dir(dir_path, recursive=True, if_non_existent="raise")


@pytest.fixture(scope="module")
def json_setup_func(work_dir) -> t.Callable[[t.Dict], fs_ops.FilePath]:
    fp = fs_ops.FilePath.model_validate(Path(__file__).parent.joinpath("file.json"))
    fp.delete(if_non_existent="return")

    def _func(data: t.Dict) -> fs_ops.FilePath:
        json_content = json.dumps(data).encode()
        fp.write(json_content)
        return fp

    yield _func
    fp.delete(if_non_existent="return")


@pytest.fixture(scope="module")
def text_setup_func(work_dir) -> t.Callable[[str], fs_ops.FilePath]:
    fp = fs_ops.FilePath.model_validate(Path(__file__).parent.joinpath("file.txt"))
    fp.delete(if_non_existent="return")

    def _func(data: str) -> fs_ops.FilePath:
        fp.write(data)
        return fp

    yield _func
    fp.delete(if_non_existent="return")


def test_file_ext_constraint_val(json_setup_func, text_setup_func):
    @pydantic.validate_call
    def _json_only(
            fp: t.Annotated[fs_ops.FilePath, fs_ops.constraints.FileExtConstraint("json")]
    ) -> t.Dict:
        with fp.open("rb") as _f:
            data = json.load(_f)
        return data

    expected_data = {
        "k1": "a",
        "k2": "b"
    }

    json_path = json_setup_func(expected_data)
    text_path = text_setup_func("xxx")

    found_data = _json_only(
        fp=json_path
    )
    assert found_data == expected_data

    # todo: should raise Validation Error but will raise json decoder error for now
    with pytest.raises(pydantic.ValidationError):
        _json_only(text_path)
