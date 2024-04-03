import pytest
import os
import typing as t
from pathlib import Path

from spice_rack import fs_ops


@pytest.fixture(scope="module")
def sample_dir() -> Path:
    p = Path(__file__).parent.parent.parent.joinpath("deferred_test_dir")
    p.mkdir(exist_ok=True)
    yield p


@pytest.fixture(scope="module")
def deferred_path_maker(sample_dir) -> t.Callable[[str], str]:
    key = "DEFERRED_TEST"
    os.environ[key] = str(sample_dir)

    def func(rel_path: str):
        return f"${key}/{rel_path}"
    return func


def test_deferred_dir_parse(deferred_path_maker, sample_dir):
    top_level = deferred_path_maker("")

    deferred_dir_obj = fs_ops.DeferredDirPath.model_validate(top_level)
    assert deferred_dir_obj.env_var_key == "DEFERRED_TEST"
    assert deferred_dir_obj.rel_path is None

    dir_obj = deferred_dir_obj.evaluate()
    assert dir_obj.as_str() == str(sample_dir) + "/"


def test_deferred_file_parse(deferred_path_maker, sample_dir):
    fp = deferred_path_maker("file.txt")

    deferred_file_obj = fs_ops.DeferredFilePath.model_validate(fp)
    assert deferred_file_obj.env_var_key == "DEFERRED_TEST"
    assert deferred_file_obj.rel_path == "file.txt"

    file_obj = deferred_file_obj.evaluate()
    assert file_obj.as_str() == str(sample_dir) + "/" + "file.txt"


def test_dir_auto_eval(deferred_path_maker):
    top_level = deferred_path_maker("")

    deferred_dir_obj = fs_ops.DeferredDirPath.model_validate(top_level)
    dir_obj_evaluated = deferred_dir_obj.evaluate()

    dir_obj_parsed = fs_ops.DirPath.model_validate(top_level)

    assert dir_obj_evaluated.as_str() == dir_obj_parsed.as_str()


def test_file_auto_eval(deferred_path_maker):
    fp = deferred_path_maker("file.txt")

    deferred_file_obj = fs_ops.DeferredFilePath.model_validate(fp)
    file_obj_evaluated = deferred_file_obj.evaluate()

    file_obj_parsed = fs_ops.FilePath.model_validate(fp)
    assert file_obj_evaluated.as_str() == file_obj_parsed.as_str()


def test_deferred_dir_parse_nested(deferred_path_maker, sample_dir):
    top_level = deferred_path_maker("nested_dir/")

    deferred_dir_obj = fs_ops.DeferredDirPath.model_validate(top_level)
    assert deferred_dir_obj.env_var_key == "DEFERRED_TEST"
    assert deferred_dir_obj.rel_path == "nested_dir/"

    dir_obj = deferred_dir_obj.evaluate()
    assert dir_obj.as_str() == str(sample_dir) + "/nested_dir/"
