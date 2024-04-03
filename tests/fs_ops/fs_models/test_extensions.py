import pytest
from pathlib import Path
import pydantic
import typing as t
import json
import yaml

from spice_rack import fs_ops


@pytest.fixture(scope="module")
def file_system() -> fs_ops.file_systems.LocalFileSystem:
    return fs_ops.file_systems.LocalFileSystem()


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
def yaml_setup_func(work_dir) -> t.Callable[[t.Dict], fs_ops.FilePath]:
    fp = fs_ops.FilePath.model_validate(Path(__file__).parent.joinpath("file.yaml"))
    fp.delete(if_non_existent="return")

    def _func(data: t.Dict) -> fs_ops.FilePath:
        with fp.open("wb") as f:
            yaml.dump(data, f, encoding="utf-8")
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


def test_json_file(json_setup_func, text_setup_func):
    @pydantic.validate_call
    def _json_only(
            fp: fs_ops.JsonFilePath
    ) -> t.Dict:
        return fp.json_read()

    expected_data = {
        "k1": "a",
        "k2": "b"
    }

    json_path = json_setup_func(expected_data)
    text_path = text_setup_func("xxx")

    found_data = _json_only(
        fp=json_path  # noqa should be coerced
    )
    assert found_data == expected_data

    # todo: should raise Validation Error but will raise json decoder error for now
    with pytest.raises(pydantic.ValidationError):
        _json_only(text_path)


def test_yaml_file(yaml_setup_func, text_setup_func):
    @pydantic.validate_call
    def _yaml_only(
            fp: fs_ops.YamlFilePath
    ) -> t.Dict:
        return fp.yaml_read()

    expected_data = {
        "k1": "a",
        "k2": "b"
    }

    yaml_path = yaml_setup_func(expected_data)
    text_path = text_setup_func("xxx")

    found_data = _yaml_only(
        fp=yaml_path  # noqa should be coerced
    )
    assert found_data == expected_data

    # todo: should raise Validation Error but will raise json decoder error for now
    with pytest.raises(pydantic.ValidationError):
        _yaml_only(text_path)
