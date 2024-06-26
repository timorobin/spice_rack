import pytest

from spice_rack import fs_ops, gcp_auth


@pytest.fixture(scope="module")
def file_system(service_account_key_data) -> fs_ops.file_systems.GcsFileSystem:
    auth_strat = gcp_auth.auth_strategies.ServiceAcctKeyAuthStrategy(
        key_data=service_account_key_data  # noqa
    )
    return fs_ops.file_systems.GcsFileSystem(
        creds=gcp_auth.AnyGcpAuthStrat.model_validate(auth_strat)
    )


@pytest.fixture(scope="module")
def work_dir(protected_bucket, file_system) -> fs_ops.path_strs.AbsoluteDirPathStr:
    p = protected_bucket + "test_dir/"
    p = file_system.clean_raw_path_str(p)
    dir_path = fs_ops.path_strs.AbsoluteDirPathStr(p)

    # if something interferes with previous test's cleanup
    file_system.delete_dir(dir_path, if_non_existent="return", recursive=True)

    file_system.make_dir(dir_path, if_exists="raise")
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
