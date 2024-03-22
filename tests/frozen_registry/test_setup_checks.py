import pytest
from typing import Type

from spice_rack import bases, frozen_registry


def test_item_no_key():
    class Item(bases.ValueModelBase):
        not_key_field: str

    # subclass init will raise a value error
    with pytest.raises(ValueError):
        class ItemNoKeyRegistry(frozen_registry.FrozenRegistryBase[Item, str]):
            ...


def test_different_key_types():
    class Item(bases.ValueModelBase):
        key: str

    class DifferentStr(bases.SpecialStrBase):
        @classmethod
        def _format_str(cls, root_data: str) -> str:
            return root_data

    # subclass init will raise a value error
    with pytest.raises(ValueError):
        class DiffKeyTypeRegistry(frozen_registry.FrozenRegistryBase[Item, DifferentStr]):
            @classmethod
            def get_key_cls(cls) -> Type[DifferentStr]:
                return DifferentStr
