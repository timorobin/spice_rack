from __future__ import annotations
import typing as t
from pydantic import PrivateAttr
from pydantic.v1.fields import DeferredType

from spice_rack import _bases, _utils
from spice_rack._frozen_registry import _exceptions

__all__ = (
    "FrozenRegistryBase",
    "FrozenRegistryOutBase",
)


# Note: the "_RegistryItemTV" class must have the specified key_attr_name attribute,
# but we can't specify this via base class, so we'll just manually check for it here.
_RegistryItemTV = t.TypeVar("_RegistryItemTV", bound=_bases.ValueModelBase)
_RegistryItemKeyTV = t.TypeVar("_RegistryItemKeyTV", bound=str)
Self = t.TypeVar("Self", bound="FrozenRegistryBase")


class FrozenRegistryBase(
    _bases.RootModel[tuple[_RegistryItemTV, ...]],
    t.Generic[_RegistryItemTV, _RegistryItemKeyTV]
):
    """
    Base class for a registry of items, where we can control how we get and add things to it.
    We use this pattern in various places, so consolidating behavior to a base class here
    minimizes the small code drift between the different implementations.

    Notes:
        - Specify the subclass kwarg 'is_base' as True to delay the item class validation
          otherwise performed in '__init_subclass__'

    """
    _distinct_keys: set[_RegistryItemKeyTV] = PrivateAttr(default=None)

    def __init_subclass__(
            cls,
            is_base: bool = False,
            **kwargs
    ) -> None:
        super().__init_subclass__(**kwargs)
        if not is_base:
            _validate_item_cls(cls)
        return

    @classmethod
    def get_key_attr_name(cls) -> str:
        """overwrite this to customize the attr we use as the key for each item"""
        return "key"

    def _post_init_setup(self) -> None:
        _distinct_keys = set(
            self._get_item_key_val(item) for item in self.iter_items()
        )
        self._distinct_keys = _distinct_keys  # noqa

    def _post_init_validation(self) -> None:
        # validate the item class post init, rather than init subclass
        _validate_item_cls(self.__class__)
        assert self._distinct_keys is not None, \
            f"'{self.get_cls_name()}' didn't set _distinct_keys private attr"

        # ensure no dupe keys
        key_set: set[_RegistryItemKeyTV] = set()
        dupe_keys: dict[_RegistryItemKeyTV, int] = {}
        for item in self.iter_items():
            item_key = self._get_item_key_val(item)
            if item_key in key_set:
                # must be at least 1
                num_appearances = dupe_keys.get(item_key, 1)
                dupe_keys[item_key] = num_appearances + 1
            else:
                key_set.add(item_key)
        if dupe_keys:
            raise _exceptions.DuplicateKeysInRegistryException(
                registry_type=type(self),
                duplicate_keys=dupe_keys,
                extra_info={}
            )

    @classmethod
    def _get_default_value(cls) -> tuple[_RegistryItemTV, ...]:
        return ()

    @classmethod
    def init_empty(cls: t.Type[Self]) -> Self:
        return cls(root=())

    @classmethod
    def get_item_cls(cls) -> t.Type[_RegistryItemTV]:
        item_ann = t.get_args(cls.model_fields["root"].annotation)[0]
        if isinstance(item_ann, t.TypeVar):
            raise ValueError(f"'{cls.get_cls_name()}' hasn't set their item type var yet")
        else:
            return item_ann

    @classmethod
    def get_key_cls(cls) -> t.Type[_RegistryItemKeyTV]:
        """default behavior is str, but we can customize this by overwriting this class-method"""
        return str

    def _get_item_key_val(self, item: _RegistryItemTV) -> _RegistryItemKeyTV:
        key_val = getattr(item, self.get_key_attr_name())
        return _utils.check_type(key_val, self.get_key_cls())

    @classmethod
    def _items_equal(cls, item1: _RegistryItemTV, item2: _RegistryItemTV) -> bool:
        """
        default behavior is direct equality, overwrite this to customize behavior of the
        registry __eq__ dunder
        """
        return item1 == item2

    def size(self) -> int:
        return len(self.root)

    def iter_items(self: Self) -> t.Iterator[_RegistryItemTV]:
        """iterator over all items"""
        for obj in self.root:
            yield obj

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, ix: int) -> _RegistryItemTV:
        try:
            return self.root[ix]
        except Exception as e:
            raise _exceptions.ItemIndexInvalidException(
                invalid_ix=ix,
                registry_type=type(self),
                registry_size=self.size(),
                caught_exception=e,
                verbose=True,
                extra_info={}
            )

    def __iter__(self: Self) -> t.Iterator[_RegistryItemTV]:
        for item in self.iter_items():
            yield item

    def list_keys(self: Self) -> list[_RegistryItemKeyTV]:
        """
        Returns: list all keys in the registry
        """
        return list(self._distinct_keys)

    def get_item_maybe(self: Self, __key: _RegistryItemKeyTV) -> t.Optional[_RegistryItemTV]:
        """
        get an item for the key or return None if nothing is found

        Args:
            __key: the key we're looking for

        Returns: an instance of _RegistryItemTV or None
        """
        for obj in self.iter_items():
            if self._get_item_key_val(obj) == __key:
                return obj
        return

    def get_item(self, __key: _RegistryItemKeyTV) -> _RegistryItemTV:
        """
        get an item for the key, or raise an exception

        Args:
            __key: the key we're looking for

        Returns: an instance of _RegistryItemTV

        Raises:
            KeyNotFoundException: if nothing is found
        """
        item_maybe = self.get_item_maybe(__key)
        if item_maybe is None:
            raise _exceptions.KeyNotFoundException(
                missing_key=__key,
                registry_type=type(self),
                keys_in_registry=self.list_keys(),
                extra_info={}
            )
        else:
            return item_maybe

    def key_exists(self, __key: _RegistryItemKeyTV) -> bool:
        return __key in self._distinct_keys

    def raise_if_found(self, __key: _RegistryItemKeyTV) -> None:
        """
        convenience method that raises an exception if the key is found

        Raises:
            KeyAlreadyExistsException: if key is found
        """
        if __key in self._distinct_keys:
            raise _exceptions.KeyAlreadyExistsException(
                duplicate_key=__key,
                registry_type=type(self),
                extra_info={}
            )

    def raise_if_not_found(self, __key: _RegistryItemKeyTV) -> None:
        """
        convenience method that raises an exception if the key is not found

        Raises:
            KeyNotFoundException: if key is found
        """
        if __key not in self._distinct_keys:
            raise _exceptions.KeyNotFoundException(
                missing_key=__key,
                registry_type=type(self),
                keys_in_registry=self.list_keys(),
                extra_info={}
            )

    def with_new_items(
            self: Self,
            new_items: list[_RegistryItemTV],
            if_exists: t.Literal["raise", "replace", "skip"] = "replace"
    ) -> Self:
        """
        create a new instance of this registry with the new items, raising an exception if
        an item already exists with the same key and 'if_exists' equals 'raise'

        Args:
            new_items: the list of items we are adding
            if_exists: if 'raise' we raise an exception if an item already exists with this key,
                and if 'replace', we replace the existing item with the new item,
                if "skip", we don't add the new item, but don't raise an error either

        Returns: a new instance of this class

        Raises:
            KeyAlreadyExistsException: an item with the same key as the new item already exists
                and 'if_exists' is set to 'raise'
        """

        # remake the key set as we add each item, so duplicates within the group of new
        # items don't make their way in.
        item_dict: dict[_RegistryItemKeyTV, _RegistryItemTV] = {
            self._get_item_key_val(item): item for item in self.iter_items()
        }
        for new_item_i in new_items:
            new_item_i_key = self._get_item_key_val(new_item_i)

            if new_item_i_key in item_dict:
                if if_exists == "raise":
                    raise _exceptions.KeyAlreadyExistsException(
                        duplicate_key=new_item_i_key,
                        registry_type=type(self),
                        extra_info={}
                    )
                elif if_exists == "replace":
                    item_dict[new_item_i_key] = new_item_i

                elif if_exists == "skip":
                    continue

                else:
                    raise ValueError(f"unexpected value for 'if_exists': '{if_exists}'")
            else:
                item_dict[new_item_i_key] = new_item_i

        return t.cast(Self, self.__class__(tuple(item_dict.values())))

    def without_items(
            self: Self,
            keys: list[_RegistryItemKeyTV],
            if_not_found: t.Literal["raise", "continue"] = "continue"
    ) -> Self:
        """
        create a new registry, without the item tied to the key specified

        Args:
            keys: the list of keys to the items we are deleting
            if_not_found: if 'raise', we raise an error if nothing exists with a key,
                and if 'continue' we just move forward as if we deleted it.

        Returns: the new instance of Self

        Raises:
            KeyNotFoundException: if nothing is found for a key, and 'if_not_found' is 'raise'
        """

        # make a set of keys to check against
        keys_to_delete: set[_RegistryItemKeyTV] = set()
        for key_i in keys:
            if key_i not in self._distinct_keys:
                if if_not_found == "raise":
                    # will raise for us
                    self.raise_if_not_found(key_i)
                else:
                    continue
            else:
                keys_to_delete.add(key_i)

        updated_items: list[_RegistryItemTV] = []
        for item in self.iter_items():
            if self._get_item_key_val(item) in keys_to_delete:
                continue
            else:
                updated_items.append(item)
        res = type(self)(tuple(updated_items))
        return t.cast(Self, res)

    def with_new_item(
            self: Self,
            new_item: _RegistryItemTV,
            if_exists: t.Literal["raise", "replace", "skip"] = "replace"
    ) -> Self:
        """
        create a new instance of this registry with a new item, raising an exception if
        an item already exists with the same key and 'if_exists' equals 'raise'

        Args:
            new_item: the item we are adding
            if_exists: if 'raise' we raise an exception if an item already exists with this key,
                and if 'replace', we replace the existing item with the new item,
                if "skip", we don't add the new item, but don't raise an error either

        Returns: a new instance of this class

        Raises:
            KeyAlreadyExistsException: an item with the same key as the new item already exists
                and 'if_exists' is set to 'raise'
        """
        return self.with_new_items(new_items=[new_item], if_exists=if_exists)

    def without_item(
            self: Self,
            key: _RegistryItemKeyTV,
            if_not_found: t.Literal["raise", "continue"] = "continue"
    ) -> Self:
        """
        create a new registry, without the item tied to the key specified

        Args:
            key: key to the item we are deleting
            if_not_found: if 'raise', we raise an error if nothing exists with this key,
                and if 'continue' we just move forward as if we deleted it.

        Returns: the new instance of Self

        Raises:
            KeyNotFoundException: if nothing is found for the key, and 'if_not_found' is 'raise'
        """
        return self.without_items(keys=[key], if_not_found=if_not_found)

    def __eq__(self: Self, other: t.Any) -> bool:
        if isinstance(other, type(self)):

            # if different size, we know not equal
            if self.size() != other.size():
                return False

            # check same keys
            self_keys = set(self.list_keys())
            other_keys = set(other.list_keys())

            # extra and missing from the POV of self,
            #   i.e. extra_keys = keys in "self" not in "other"
            extra_keys, missing_keys = _utils.get_difference_between_sets(
                self_keys, other_keys
            )
            if extra_keys or missing_keys:
                return False

            # check each object individually
            for key in self_keys:
                self_obj = self.get_item(key)
                other_obj = other.get_item(key)
                if not self._items_equal(self_obj, other_obj):
                    return False

            # if we make it here, they are equal
            return True
        else:

            # not same type, so definitely False
            return False

    def special_repr(self: Self) -> str:
        return (f"{self.__class__.__name__}"
                f"[key_field='{self.get_key_attr_name()}', size={self.size()}]")


def _validate_item_cls(_registry_cls: t.Type[FrozenRegistryBase]) -> None:
    """
    Executes some manual checks that the registry's item class meets the requirements expected by
    the frozen registry container
    """
    # this means it is the intermediate/passthrough type made when we set up a class with a
    # parameterized base. We skip this validation in this case
    if _registry_cls.get_cls_name().startswith("FrozenRegistryBase["):
        return

    # this is a concrete frozen registry class, i.e. one we plan to instantiate and use.

    # Check the item type isn't a generic, i.e. the type var has been replaced with a proper class.
    item_cls = _registry_cls.get_item_cls()

    # todo: this DeferredType check might be unnecessary in pydantic v2.
    if isinstance(item_cls, DeferredType):
        raise ValueError(
            f"'{_registry_cls.get_cls_name()}' has a deferred type for the item class still"
        )

    elif isinstance(item_cls, t.TypeVar):
        raise ValueError(
            f"'{_registry_cls.get_cls_name()}' has a type var as the item type still, {item_cls}"
        )
    else:

        # make sure the object has a 'key' attribute with the correct annotation
        # this must be either a pydantic field or a property-decorated method
        item_cls = _utils.check_subclass(item_cls, _bases.ValueModelBase)
        key_attr_name = _registry_cls.get_key_attr_name()
        key_field_cls = _registry_cls.get_key_cls()

    # check if pydantic field
        if key_attr_name in item_cls.model_fields:
            key_field = item_cls.model_fields[key_attr_name]
            key_field_type_ann = key_field.annotation
            if key_field_type_ann != key_field_cls:
                raise ValueError(
                    f"the key field type ann must equal the key field class"
                    f"specified in this registry. "
                    f"We encountered {key_field_type_ann} and {key_field_cls}"
                )

        # check if defined as a property
        elif hasattr(item_cls, key_attr_name):

            # could be any type of class attribute
            key_method = getattr(item_cls, key_attr_name)

            # todo: could also add support for a no-arg method, but for now just tell user to make it a property
            # make sure a property-decorated function, with the correct return annotation
            if isinstance(key_method, property):
                getter_func: t.Callable = key_method.fget
                _getter_anns: t.Dict = t.get_type_hints(getter_func)
                if "return" not in _getter_anns:
                    raise ValueError(
                        f"You must specify a return annotation for the '{key_attr_name}' "
                        f"property on the '{item_cls.get_cls_name()}'to use it as a key"
                    )

                return_ann = _getter_anns["return"]
                if return_ann != key_field_cls:
                    raise ValueError(
                        f"'{key_attr_name}' on the '{item_cls.get_cls_name()}' maps to a property "
                        f"with a return annotation of '{return_ann}', and the '{_registry_cls.get_cls_name()}' "
                        f"registry class expects the key field to be type {key_field_cls}."
                    )

            # not a property
            else:
                raise ValueError(
                    f"the specified key attribute, '{key_attr_name}', must be either a pydantic field or a property,"
                    f" and the '{item_cls.get_cls_name()}' class defined the '{key_attr_name}' "
                    f"attribute as type {type(key_method)}"
                )

        # not found at all
        else:
            raise ValueError(
                f"'{item_cls.get_cls_name()}' doesn't have a '{key_attr_name}' field or property specified"
            )

        return None


class FrozenRegistryOutBase(_bases.RootModel[t.List[_RegistryItemTV]], t.Generic[_RegistryItemTV]):
    """base class for an api response model for a frozen registry"""
    ...
