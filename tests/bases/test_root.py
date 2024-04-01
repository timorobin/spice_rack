import pytest
import pydantic

from spice_rack import bases


class NoDefaultRoot(bases.RootModel[str]):
    ...


class RootWithDefault(bases.RootModel[str]):
    @classmethod
    def _get_default_value(cls) -> str:
        return "xxx"


def test_no_default():
    with pytest.raises(pydantic.ValidationError):
        NoDefaultRoot()

    a = NoDefaultRoot("xxx")
    assert a.root == "xxx"
    assert a.model_dump() == "xxx"


def test_default_root():
    a = RootWithDefault()
    assert a.root == "xxx"
    assert a.model_dump() == "xxx"

    b = RootWithDefault("xxx")
    assert a == b
