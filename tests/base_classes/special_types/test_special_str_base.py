import pytest
import json
import typing as t

from pydantic import BaseModel

from spice_rack import base_classes


class SomeSpecialStr(base_classes.special_types.SpecialStrBase):
    _blocked_vals: t.ClassVar[list[str]] = ["X", "Y"]

    @classmethod
    def _parse_non_str(cls, root_data: t.Any) -> str:
        if isinstance(root_data, int):
            return str(root_data)
        else:
            return super()._parse_non_str(root_data)

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
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

    with pytest.raises(TypeError):
        SomeSpecialStr(1.0)


def test_ide():
    """
    Tests visually that the IDE behaves as expected.
    This can't really fail at test time like normal tests, must be evaluated visually.
    """
    # your IDE should not highlight this one bc string is ok
    assert SomeSpecialStr("a")

    with pytest.raises(TypeError):
        # your IDE should highlight this one bc the param doesn't have int in it
        SomeSpecialStr(1.90)


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
