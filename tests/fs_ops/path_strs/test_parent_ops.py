from spice_rack import fs_ops


def test_get_parent_rel_file():
    fp = fs_ops.path_strs.RelFilePathStr("some/rel/path.txt")
    parent = fp.get_parent()
    assert parent == fs_ops.path_strs.RelDirPathStr("some/rel/")
    assert parent.joinpath("path.txt") == fp


def test_get_parent_abs_file():
    fp = fs_ops.path_strs.AbsoluteFilePathStr("/some/abs/path.txt")
    parent = fp.get_parent()
    assert parent == fs_ops.path_strs.AbsoluteDirPathStr("/some/abs/")
    assert parent.joinpath("path.txt") == fp


def test_get_parent_rel_file_no_parent():
    fp = fs_ops.path_strs.RelFilePathStr("top_level_file.txt")
    parent = fp.get_parent()
    assert parent == fs_ops.path_strs.RelDirPathStr("./")
    assert parent.joinpath("top_level_file.txt") == fp


def test_get_parent_abs_file_no_parent():
    fp = fs_ops.path_strs.AbsoluteFilePathStr("/top_level_file.txt")
    parent = fp.get_parent()
    assert parent == fs_ops.path_strs.AbsoluteDirPathStr("/")
    assert parent.joinpath("top_level_file.txt") == fp
