import pytest
import json
from typing import ClassVar

from pydantic import BaseModel

from spice_rack import base_classes


class SomeSpecialStr(base_classes.special_types.special_str_base.AbstractSpecialStr):
    _blocked_vals: ClassVar[list[str]] = ["X", "Y"]

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        data = root_data.upper()
        if data in cls._blocked_vals:
            raise ValueError(
                f"'{data}' is one of the blocked values!"
            )
        else:
            return data


def test_special_str_instance():
    raw_s = "ABC"
    assert isinstance(raw_s, str)
    assert not isinstance(raw_s, SomeSpecialStr)

    special_s = SomeSpecialStr(raw_s)
    assert isinstance(special_s, str)
    assert isinstance(special_s, SomeSpecialStr)

    # note that string comparisons still work as normal, no special formatting applied
    assert special_s == raw_s


def test_formatting_applied():
    raw_s = "abc"
    assert isinstance(raw_s, str)
    assert not isinstance(raw_s, SomeSpecialStr)

    special_s = SomeSpecialStr(raw_s)
    assert isinstance(special_s, str)
    assert isinstance(special_s, SomeSpecialStr)

    assert raw_s == "abc"
    assert special_s == "ABC"


def test_custom_init_checking():
    bad_s = "x"
    with pytest.raises(ValueError):
        SomeSpecialStr(bad_s)


class SomeClass(BaseModel):
    f: SomeSpecialStr


def test_special_str_as_field():
    inst = SomeClass(
        f="a"  # noqa - will be coerced
    )
    assert isinstance(inst.f, SomeSpecialStr)

    assert inst.f == "A"
    assert inst.dict() == {"f": "A"}

    assert SomeClass.parse_raw(inst.json()) == inst

    assert json.loads(inst.json()) == {"f": "A"}


def test_repr_vs_str():
    a = SomeSpecialStr("a")

    assert str(a) == "A"
    assert repr(a) == repr("A")
    assert a.special_repr() == "SomeSpecialStr['A']"