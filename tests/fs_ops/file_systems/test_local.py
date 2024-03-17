import pytest
from pathlib import Path

from spice_rack import fs_ops


@pytest.fixture(scope="module")
def file_system() -> fs_ops.file_systems.LocalFileSystem:
    return fs_ops.file_systems.LocalFileSystem()


# also tests make dir

@pytest.fixture(scope="function")
def work_dir(file_system) -> fs_ops.path_strs.AbsoluteDirPathStr:
    p = Path(__file__).parent.joinpath("test_dir/")
    dir_path = fs_ops.path_strs.AbsoluteDirPathStr(str(p))
    file_system.make_dir(path=dir_path, if_exists="raise")
    yield dir_path
    file_system.delete_dir(dir_path, recursive=True, if_non_existent="raise")


def test_dir_exists(file_system, work_dir):
    assert file_system.exists(work_dir)


def test_write_to_new_file(file_system, work_dir):
    fp = work_dir.joinpath("file.txt")
    assert not file_system.exists(fp)
    text = "some random text"
    with file_system.open_file(fp, "wb") as f:
        f.write(text.encode())

    with file_system.open_file(fp, "rb") as f:
        read_text = f.read().decode()

    assert read_text == text
