import pytest
from pathlib import Path

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
