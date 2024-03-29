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


def test_dir_parse(file_system, work_dir):
    from_str = fs_ops.DirPath.model_validate(str(work_dir))
    regular = fs_ops.DirPath(
        file_system=file_system, path=work_dir
    )
    assert regular == from_str


@pytest.fixture(scope="module")
def dir_obj(file_system, work_dir) -> fs_ops.DirPath:
    dir_obj = fs_ops.DirPath(
        file_system=file_system, path=work_dir
    )
    return dir_obj


def test_dir_exists(dir_obj, ):
    assert dir_obj.exists()


def test_make_dir(dir_obj,):
    sub_dir = dir_obj.joinpath("sub_folder/")
    assert not sub_dir.exists()
    sub_dir.make_self(if_exists="raise")
    assert sub_dir.exists()
    sub_dir.delete(if_non_existent="raise")
    assert not sub_dir.exists()
