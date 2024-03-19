import pytest
import spice_rack


@pytest.fixture(scope="module")
def expected_version() -> str:
    # in dev always 0.0.0
    return "0.0.0"


def test_dunder(expected_version):
    assert spice_rack.__version__ == expected_version


def test_caps(expected_version):
    assert spice_rack.VERSION == expected_version
