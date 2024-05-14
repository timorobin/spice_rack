from __future__ import annotations
import typing as t
import typing_inspect
import pydantic
from pydantic import Field
import functools

from spice_rack import _bases, _utils
from spice_rack._frozen_registry import _exceptions

__all__ = (
    "FrozenRegistryOutBase",
)


# Note: the "_RegistryItemTV" class must have the specified key_attr_name attribute,
# but we can't specify this via base class, so we'll just manually check for it here.
_RegistryItemTV = t.TypeVar("_RegistryItemTV", bound=_bases.ValueModelBase)
_RegistryItemKeyTV = t.TypeVar("_RegistryItemKeyTV", bound=str)
Self = t.TypeVar("Self", bound="FrozenRegistryBase")


class FrozenRegistryMember(_bases.ValueModelBase, t.Generic[_RegistryItemKeyTV, _RegistryItemTV]):
    """a member of a frozen registry, holding a key and an item"""
    key: _RegistryItemKeyTV = Field(description="the key we use to look up the item")
    item: _RegistryItemTV = Field(
        description="The item itself. The frozen registry is meant to simulate we have a collection of these items,"
                    " with some extra built-in functionality and safeties"
    )


class FrozenRegistryBase(
    _bases.RootModel[
        t.Tuple[FrozenRegistryMember[_RegistryItemKeyTV, _RegistryItemTV], ...]
    ],
    t.Generic[_RegistryItemTV, _RegistryItemKeyTV]
):
    """
    Base class for a registry of items, where we can control how we get and add things to it.
    We use this pattern in various places, so consolidating behavior to a base class here
    minimizes the small code drift between the different implementations.
    """
    _key_lookup: t.Dict[_RegistryItemKeyTV, int] = pydantic.PrivateAttr(default=None)

    @classmethod
    @t.final
    def _get_member_cls(cls) -> t.Type[FrozenRegistryMember[_RegistryItemKeyTV, _RegistryItemTV]]:
        root_ann = cls.model_fields["root"].annotation
        member_cls: t.Type[FrozenRegistryMember[_RegistryItemKeyTV, _RegistryItemTV]] = t.get_args(root_ann)[0]
        return member_cls

    @classmethod
    @t.final
    def is_item_cls_set(cls) -> bool:
        member_cls = cls._get_member_cls()
        item_ann = member_cls.model_fields["item"].annotation

        return not typing_inspect.is_typevar(item_ann)

    @classmethod
    @t.final
    def is_key_cls_set(cls) -> bool:
        member_cls = cls._get_member_cls()
        key_ann = member_cls.model_fields["key"].annotation
        return not typing_inspect.is_typevar(key_ann)

    @classmethod
    @t.final
    def get_item_cls(cls) -> t.Type[_RegistryItemTV]:
        """Returns the type specified, if it is a type var, this raises a ValueError"""
        member_cls = cls._get_member_cls()
        item_ann = member_cls.model_fields["item"].annotation

        if typing_inspect.is_typevar(item_ann):
            raise ValueError(
                f"'{item_ann}' is still a type var and not parameterized yet"
            )
        else:
            return item_ann

    @classmethod
    @t.final
    def get_key_cls(cls) -> t.Type[_RegistryItemKeyTV]:
        member_cls = cls._get_member_cls()
        key_ann = member_cls.model_fields["key"].annotation

        if typing_inspect.is_typevar(key_ann):
            raise ValueError(
                f"'{key_ann}' is still a type var and not parameterized yet"
            )
        else:
            return key_ann

    @classmethod
    def _key_getter_fn_spec(cls) -> t.Union[t.Callable[[_RegistryItemTV], _RegistryItemKeyTV], str]:
        """
        Convenience method to allow for specifying an attr as the getter easily, while keeping our error messaging
        in the '_key_getter_func_builder'.

        overwrite this to customize how get the key from the item.
        This is used to automatically parse '_RegistryItemTV' instances into 'FrozenRegistryMember' instances

        If this returns a string, we assume it an attr access, i.e. if it returns "key" the function used will
        be getattr(item, "key"). If callable, we'll just use the callable directly
        """
        return "key"

    @classmethod
    @functools.lru_cache(maxsize=1)
    @t.final
    def _key_getter_fn_builder(cls) -> t.Callable[[_RegistryItemTV], _RegistryItemKeyTV]:
        """this returns the actual function we'll use to get the key"""
        getter_fn = cls._key_getter_fn_spec()

        final_fn: t.Callable[[_RegistryItemTV], _RegistryItemKeyTV]
        if isinstance(getter_fn, str):
            attr_name = getter_fn
            # make sure either a property or a pydantic field
            item_cls: pydantic.BaseModel = cls.get_item_cls()

            if attr_name not in item_cls.model_fields and not hasattr(item_cls, attr_name):
                raise ValueError(
                    f"attr name specified, '{attr_name}', not found on the item cls {item_cls} "
                )

            def final_fn(__item: _RegistryItemTV) -> _RegistryItemKeyTV:
                return getattr(__item, getter_fn)
        else:
            final_fn = getter_fn

        return final_fn

    @classmethod
    def validate_class_setup(cls) -> None:
        # make sure we can build this key getter function
        cls._key_getter_fn_builder()

    def __init_subclass__(cls, **kwargs):
        # if base we don't validate
        if cls.is_key_cls_set() and cls.is_item_cls_set():
            cls.validate_class_setup()

        super().__init_subclass__(**kwargs)

    @classmethod
    def _item_to_member(cls, __item: t.Any) -> FrozenRegistryMember[_RegistryItemKeyTV, _RegistryItemTV]:
        item = cls.get_item_cls().model_validate(__item)
        key = cls._key_getter_fn_builder()(item)
        return FrozenRegistryMember[cls.get_key_cls(), cls.get_item_cls()](
            key=key,
            item=item
        )

    # noinspection PyNestedDecorators
    @pydantic.field_validator("root", mode="before")
    @classmethod
    def _auto_parse_items(cls, data: t.Any) -> t.Any:
        if isinstance(data, (list, tuple)):
            members: t.List[t.Dict] = []
            for obj in data:
                if isinstance(obj, FrozenRegistryMember):
                    members.append({"key": obj.key, "item": obj.item})
                else:
                    member = cls._item_to_member(obj)
                    members.append(member)
            data = members
        return data

    @classmethod
    def _get_default_value(cls) -> tuple[FrozenRegistryMember, ...]:
        return ()

    @classmethod
    def init_empty(cls: t.Type[Self]) -> Self:
        return cls(root=())

    def _post_init_setup(self) -> None:
        self._key_lookup = {
            member.key: member_ix for member_ix, member in enumerate(self.iter_members())
        }

    def size(self) -> int:
        return len(self.root)

    def iter_members(self) -> t.Iterator[FrozenRegistryMember[_RegistryItemTV, _RegistryItemKeyTV]]:
        for member in self.root:
            yield member

    def iter_items(self: Self) -> t.Iterator[_RegistryItemTV]:
        """iterator over all items"""
        for member in self.iter_members():
            yield member.item

    def __len__(self) -> int:
        return self.size()

    def __getitem__(self, ix: int) -> _RegistryItemTV:
        try:
            return self.root[ix].item
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
        return list(self._key_lookup.keys())

    def get_item_maybe(self, __key: _RegistryItemKeyTV) -> t.Optional[_RegistryItemTV]:
        """
        get an item for the key or return None if nothing is found

        Args:
            __key: the key we're looking for

        Returns: an instance of _RegistryItemTV or None
        """
        __key = self.get_key_cls()(__key)
        if __key in self._key_lookup:
            member_ix = self._key_lookup[__key]
            return self.root[member_ix].item
        else:
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
        return __key in self._key_lookup

    def raise_if_found(self, __key: _RegistryItemKeyTV) -> None:
        """
        convenience method that raises an exception if the key is found

        Raises:
            KeyAlreadyExistsException: if key is found
        """
        if __key in self._key_lookup:
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
        if __key not in self._key_lookup:
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
        curr_members: dict[_RegistryItemKeyTV, FrozenRegistryMember[_RegistryItemKeyTV, _RegistryItemTV]] = {
            member.key: member for member in self.iter_members()
        }
        new_members: t.List[FrozenRegistryMember] = [
            self._item_to_member(item) for item in new_items
        ]

        for new_member_i in new_members:
            if new_member_i.key in curr_members:
                if if_exists == "raise":
                    raise _exceptions.KeyAlreadyExistsException(
                        duplicate_key=new_member_i.key,
                        registry_type=type(self),
                        extra_info={}
                    )
                elif if_exists == "replace":
                    curr_members[new_member_i.key] = new_member_i

                elif if_exists == "skip":
                    continue

                else:
                    raise ValueError(f"unexpected value for 'if_exists': '{if_exists}'")
            else:
                curr_members[new_member_i.key] = new_member_i

        return t.cast(
            Self, self.__class__(tuple(curr_members.values()))
        )

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
            if key_i not in self._key_lookup:
                if if_not_found == "raise":
                    # will raise for us
                    self.raise_if_not_found(key_i)
                else:
                    continue
            else:
                keys_to_delete.add(key_i)

        updated_members: list[FrozenRegistryMember] = []
        for member in self.iter_members():
            if member.key in keys_to_delete:
                continue
            else:
                updated_members.append(member)
        res = type(self)(tuple(updated_members))
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
                if not self_obj == other_obj:
                    return False

            # if we make it here, they are equal
            return True
        else:

            # not same type, so definitely False
            return False

    def special_repr(self: Self) -> str:
        return (f"{self.__class__.__name__}"
                f"[key_field='{self.get_key_attr_name()}', size={self.size()}]")
