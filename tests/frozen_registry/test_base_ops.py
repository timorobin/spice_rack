import pytest
from typing import Type

from spice_rack import bases, frozen_registry


class KeyStr(bases.special_str.StrKeyBase):

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        return root_data.upper()


class Item(bases.ValueModelBase):
    custom_key_field_name: KeyStr
    f: str


class Registry(
    frozen_registry.FrozenRegistryBase[Item, KeyStr],
):
    @classmethod
    def get_key_cls(cls) -> Type[KeyStr]:
        return KeyStr

    @classmethod
    def _key_getter_fn_spec(cls) -> str:
        return "custom_key_field_name"


@pytest.fixture(scope="module")
def item1() -> Item:
    return Item(custom_key_field_name=KeyStr("item1"), f="x")


@pytest.fixture(scope="module")
def item2() -> Item:
    return Item(custom_key_field_name=KeyStr("item2"), f="x")


@pytest.fixture(scope="module")
def item1_v2(item1) -> Item:
    """item1 key but different data otherwise"""
    return Item(
        custom_key_field_name=item1.custom_key_field_name,
        f="z"
    )


def test_init_empty() -> None:
    reg = Registry.init_empty()
    assert isinstance(reg, Registry)
    assert reg.size() == 0


def test_add_item(item1) -> None:
    reg = Registry.init_empty()
    assert reg.size() == 0

    new_reg = reg.with_new_item(new_item=item1, if_exists="replace")

    # original registry unchanged, new instance created
    assert reg.size() == 0
    assert new_reg.size() == 1


def test_add_dupe_raise(item1, item1_v2) -> None:
    reg = Registry.init_empty()
    assert reg.size() == 0

    new_reg = reg.with_new_item(new_item=item1, if_exists="raise")
    assert new_reg.size() == 1

    with pytest.raises(frozen_registry.exceptions.KeyAlreadyExistsException):
        new_reg.with_new_item(new_item=item1_v2, if_exists="raise")


def test_add_item_replace(item1, item2, item1_v2) -> None:
    reg = Registry()
    assert reg.size() == 0

    new_reg = reg.with_new_items(new_items=[item1, item2], if_exists="raise")
    assert new_reg == Registry.model_validate([item1, item2])

    # keys the same but item is different
    new_new_reg = new_reg.with_new_item(new_item=item1_v2, if_exists="replace")
    assert set(new_reg.list_keys()) == {"ITEM1", "ITEM2"}
    assert set(new_new_reg.list_keys()) == {"ITEM1", "ITEM2"}


def test_get_item(item1) -> None:
    reg = Registry.init_empty()
    assert reg.size() == 0

    new_reg = reg.with_new_item(new_item=item1, if_exists="raise")
    assert new_reg.size() == 1
    item1 = new_reg.get_item(KeyStr("item1"))
    assert item1

    # note pycharm raise type checker highlight, but not raise an exception bc it will be
    # reformatted
    item1 = new_reg.get_item("item1")
    assert item1

    with pytest.raises(frozen_registry.exceptions.KeyNotFoundException):
        new_reg.get_item(KeyStr("item1000"))

    # 'get_item_maybe' returns none and 'get_item' raises
    item2_maybe = new_reg.get_item_maybe(KeyStr("item2"))
    assert item2_maybe is None

    with pytest.raises(frozen_registry.exceptions.KeyNotFoundException):
        new_reg.get_item(KeyStr("item2"))


def test_bracket_style_get(item1, item2) -> None:
    reg = Registry()
    assert reg.size() == 0
    with pytest.raises(frozen_registry.exceptions.ItemIndexInvalidException):
        _ = reg[0]

    new_reg = reg.with_new_item(new_item=item1, if_exists="raise")
    assert new_reg.size() == 1
    assert new_reg[0] == item1

    with pytest.raises(frozen_registry.exceptions.ItemIndexInvalidException):
        _ = new_reg[1]

    new_new_reg = new_reg.with_new_item(item2)

    assert new_new_reg[1] == new_new_reg[-1]
