import pytest
from pathlib import Path
import typing as t
import json

from spice_rack import fs_ops


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


def test_file_parse(file_system, work_dir):
    file_path_str = work_dir.joinpath("file.txt")

    from_str = fs_ops.FilePath.model_validate(str(file_path_str))
    regular = fs_ops.FilePath(
        file_system=file_system, path=file_path_str
    )
    assert regular == from_str


@pytest.fixture(scope="module")
def file_obj(file_system, work_dir) -> fs_ops.FilePath:
    file_path_str = work_dir.joinpath("file.txt")
    file_obj = fs_ops.FilePath(
        file_system=file_system, path=file_path_str
    )

    yield file_obj
    file_obj.delete(if_non_existent='return')


def test_file_exists(file_obj, ):
    assert not file_obj.exists()


def test_create_file(file_obj):
    assert not file_obj.exists()
    file_obj.write(data="some_text", mode="wb")
    assert file_obj.exists()


def test_read_text(file_obj):
    data = "some text"
    file_obj.delete(if_non_existent="return")
    file_obj.write(data, mode="wb")
    data_found = file_obj.read_as_str()
    assert data_found == data


def test_file_parse_gcs(public_bucket):
    public_bucket_file = public_bucket + "file.txt"
    from_str = fs_ops.FilePath.model_validate(public_bucket_file)
    inferred_fs = from_str.file_system  # noqa -- pycharm AI is shitty
    assert isinstance(inferred_fs, fs_ops.file_systems.GcsFileSystem), type(inferred_fs)


def test_dir_path_kwarg_only(work_dir):
    p = str(work_dir)
    fs_obj = fs_ops.DirPath.model_validate({"path": p})
    assert fs_obj.path == work_dir
    assert fs_obj.file_system_type == fs_ops.file_systems.LocalFileSystem.get_class_id()


def test_file_path_kwarg_only(work_dir):
    p = str(work_dir.joinpath("file.txt"))
    fs_obj = fs_ops.FilePath.model_validate({"path": p})
    assert fs_obj.path == p
    assert fs_obj.file_system_type == fs_ops.file_systems.LocalFileSystem.get_class_id()


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
