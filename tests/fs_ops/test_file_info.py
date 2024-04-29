import pytest

from spice_rack import fs_ops


def test_mime_type_from_file_ext_good():
    assert fs_ops.file_info.MimeType.from_file_ext("pdf") == 'application/pdf'


def test_mime_type_from_file_ext_unknown_mime():
    with pytest.raises(ValueError):
        fs_ops.file_info.MimeType.from_file_ext("xxx")


def test_file_ext_to_mime_type_good():
    assert fs_ops.file_info.FileExt("pdf").get_mime_type() == "application/pdf"


def test_file_ext_to_mime_type_unknown_mime():
    assert fs_ops.file_info.FileExt("xxx").get_mime_type() is None
