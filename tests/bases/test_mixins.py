import pytest

from spice_rack import bases


class Parent(bases.base_base.PydanticBase):
    f: str = "fff"


def test_guid():
    class X(Parent, bases.mixins.GuidMixin):
        ...

    # check it can be initialized with default
    x = X()
    assert x.f == "fff"
    assert x.guid

    # check serialization works
    assert x.json_dict() == {"f": "fff", "guid": str(x.guid)}

    # check we can initialize it with specified value
    x2 = X(
        guid=x.guid
    )

    assert x == x2

    with pytest.raises(AssertionError):
        assert X() == X()


def test_created_at():
    class X(Parent, bases.mixins.CreatedAtMixin):
        ...

    # check it can be initialized with default
    x = X()
    assert x.f == "fff"

    # check str casting works
    assert x.created_at_str

    # check serialization works
    assert x.json_dict() == {"f": "fff", "created_at": x.created_at_str}

    # check we can initialize it with specified value
    x2 = X(
        created_at=x.created_at
    )

    assert x == x2


def test_updated_at():
    class X(Parent, bases.mixins.UpdatedAtMixin):
        ...

    # check it can be initialized with default
    x = X()
    assert x.f == "fff"

    # check str casting works
    assert x.updated_at_str

    # check serialization works
    assert x.json_dict() == {
        "f": "fff",
        "updated_at": x.updated_at_str
    }

    # check we can initialize it with specified value
    x2 = X(
        updated_at=x.updated_at
    )

    assert x == x2


def test_updated_created_at():
    class X(Parent, bases.mixins.CreatedAtUpdatedAtMixin):
        ...

    # check it can be initialized with default
    x = X()
    assert x.f == "fff"

    # check str casting works
    assert x.updated_at_str
    assert x.created_at_str

    # check serialization works
    assert x.json_dict() == {
        "f": "fff",
        "updated_at": x.updated_at_str,
        "created_at": x.created_at_str
    }

    # check we can initialize it with specified value
    x2 = X(
        created_at=x.created_at,
        updated_at=x.updated_at
    )

    assert x == x2
