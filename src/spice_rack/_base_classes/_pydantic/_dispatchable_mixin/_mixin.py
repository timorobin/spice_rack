from __future__ import annotations
from typing import ClassVar, Type, Optional, Any, Generic, TypeVar, Iterator, Union, cast
from pydantic import BaseModel, Field, PrivateAttr, validator
from pydantic.generics import GenericModel
from pydantic.fields import ModelField

from spice_rack._base_classes._pydantic._misc import ClassNameMixin
from spice_rack._base_classes._pydantic._dispatchable_mixin import _cls_id_card


__all__ = (
    "DispatchableModelMixin",
)


# PyCharm IDE works if we do this rather than Self
Self = TypeVar("Self", bound="DispatchableModelMixin")


class DispatchableModelMixin(BaseModel, ClassNameMixin):
    """
    adds a class_id field and makes a registry for us to interact with.

    When making a new parent class, the leftmost parent class must be this class.
    """

    # this is set in _setup_dispatchable_class classmethod
    __id_card__: ClassVar[_cls_id_card.ClassIdCard] = None
    """
    Info about the class such as family tree, class type and its ID.
    """

    __family_tree__: ClassVar[Optional[FamilyTree]] = None
    """
    all children class for a given root class. This is only set for root and passthrough classes
    """

    # would be a computed field in pydantic v2
    class_id: _cls_id_card.ClassId = Field(
        description="the class id path for this class, this is never set directly, only computed",
        default="null"  # placeholder bc otherwise we can overwrite in the setup
    )

    @classmethod
    def _setup_subclass(cls, parent_cls_ix: int = 1, ) -> None:
        id_card = _setup_dispatchable_class(cls=cls, parent_cls_ix=parent_cls_ix)
        cls.__id_card__ = id_card

        # update the default value for the class id path field, so it comes up on the schema gen
        class_id_field: ModelField = cls.__fields__.get("class_id")

        if cls.get_cls_type() == "concrete":
            # todo: const is removed in pydantic v2

            class_id_field.field_info.const = True
            class_id_field.default = cls.get_class_id()
            class_id_field.field_info.default = cls.get_class_id()
            # we want Literal so we can use discriminated union
            from typing import Literal
            class_id_field.type_ = Literal[(id_card.cls_id,)]  # noqa - this is ok

        # if root, we set a new family tree
        if id_card.cls_type == "root":
            cls.__family_tree__ = FamilyTree[cls](root_cls=cls)
        else:
            cls.get_family_tree().add_member(new_member=cls)

    @validator("class_id", pre=True, )
    def _check_discrim_value(cls, v: Optional[_cls_id_card.ClassId]) -> _cls_id_card.ClassId:
        if v is None:
            v = cls.get_class_id()
        else:
            found_class_id = _cls_id_card.ClassId(v)
            if found_class_id != cls.get_class_id():
                raise ValueError(
                    f"class id doesn't line up with this class. encountered '{v}'"
                    f" and expected '{cls.get_class_id()}'"
                )
        return v

    def __init_subclass__(
            cls,
            parent_cls_ix: int = 1,
            **kwargs
    ):
        cls._setup_subclass(
            parent_cls_ix=parent_cls_ix,
        )
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_class_id_card(cls) -> _cls_id_card.ClassIdCard:
        if cls.__id_card__ is None:
            raise ValueError(f"'{cls.get_cls_name()}' doesn't have an id card set?")
        return cls.__id_card__

    @classmethod
    def get_class_id(cls) -> _cls_id_card.ClassId:
        return cls.get_class_id_card().cls_id

    @classmethod
    def get_cls_type(cls) -> _cls_id_card.ClassTypeT:
        return cls.get_class_id_card().cls_type

    @classmethod
    def get_root_cls(cls) -> Type[DispatchableModelMixin]:
        return cls.get_class_id_card().family_head

    # todo: not sure how to do typing on this bc it isn't really "self" in the family tree
    #  param unless this class is the root.
    @classmethod
    def get_family_tree(cls: Type[Self]) -> FamilyTree[DispatchableModelMixin]:
        return cls.get_root_cls().__family_tree__

    @classmethod
    def build_concrete_union_type_ann(
            cls: Type[Self],
    ) -> Type[Self]:
        """
        return a type ann that is a union of all concrete types, but "cast" it
        to the root class type for the purposes of the type checker.
        This gives us the mypy behavior as if it were the base class, but the schema
        generation behavior as if it were a union of all the concrete types.

        Examples:

        simple example::

            class AbstractExampleCls(DispatchableModelMixin, AbstractValueModel):
                ...

            class Concrete1(AbstractExampleCls):
                ...

            class Concrete2(AbstractExampleCls):
                ...

        would produce the actual annotation::

            Union[Concrete1, Concrete2]

        and the type checker would treat it as the annotation::

            Type[AbstractExampleCls]
        """
        if cls.get_cls_type() == "concrete":
            return cls

        else:
            concrete_subclasses = tuple(
                cls.get_family_tree().get_concrete_subclasses(from_member=cls)
            )

            union_type = Union[concrete_subclasses]
        res = cast(Type[Self], union_type)
        return res

    @classmethod
    def _dispatch_parse(cls: Type[Self], obj: Any) -> Self:
        if isinstance(obj, cls):
            return obj

        if isinstance(obj, BaseModel):
            obj = obj.dict()

        if isinstance(obj, dict):
            return cls.get_family_tree().dispatch_parse(data=obj, dispatching_cls=cls)

        else:
            raise ValueError(
                f"we can only dispatch parse dicts and pydantic models. "
                f"Not type {type(obj)}."
            )

    @classmethod
    def parse_obj(cls: Type[Self], obj: Any) -> Self:
        return cls._dispatch_parse(obj)

    @classmethod
    def validate(cls, obj: Any) -> Self:
        return cls._dispatch_parse(obj)


_RootClsTV = TypeVar("_RootClsTV", bound=DispatchableModelMixin)
_DispatchingClsTV = TypeVar("_DispatchingClsTV", bound=DispatchableModelMixin)


class FamilyTree(GenericModel, Generic[_RootClsTV]):
    """holds family registry"""

    class Config:
        frozen = True
        validate_assignment = True
        extra = "forbid"

    root_cls: Type[_RootClsTV] = Field(description="the root of this family tree")
    _registry: dict[_cls_id_card.ClassId, Type[_RootClsTV]] = PrivateAttr(default_factory=dict)
    """the internal registry"""

    def get_member(self, class_id: _cls_id_card.ClassId) -> Type[_RootClsTV]:
        if class_id not in self._registry:
            raise ValueError(
                f"'{class_id}' not in the registry for the '{self.root_cls}' class"
            )

        else:
            return self._registry[class_id]

    def add_member(self, new_member: Type[_RootClsTV]) -> None:
        class_id = new_member.get_class_id()

        if class_id in self._registry:
            existing_cls = self.get_member(class_id)
            msg = (f"ClassId collision:"
                   f" \n\tnew member: '{new_member}' \n\texisting class: '{existing_cls}'")
            raise ValueError(msg)

        else:
            self._registry[class_id] = new_member

    def iter_members(self) -> Iterator[Type[_RootClsTV]]:
        for member in self._registry.values():
            yield member

    def list_class_ids(
            self,
            from_member: Type[_RootClsTV],
            cls_types_only: Optional[list[_cls_id_card.ClassTypeT]] = None
    ) -> list[_cls_id_card.ClassId]:

        class_id_prefix = str(from_member.get_class_id())
        res: list[_cls_id_card.ClassId] = []
        for member_i in self.iter_members():
            if member_i.get_class_id().startswith(class_id_prefix):
                if cls_types_only is None or member_i.get_cls_type() in cls_types_only:
                    res.append(member_i.get_class_id())
        return res

    def list_concrete_class_ids(
            self,
            from_member: Type[_RootClsTV],
    ) -> list[_cls_id_card.ClassId]:
        return self.list_class_ids(
            from_member=from_member, cls_types_only=["concrete"]
        )

    def get_concrete_subclasses(
            self,
            from_member: Type[_RootClsTV],
    ) -> list[Type[_RootClsTV]]:
        res = []
        for cls_id in self.list_concrete_class_ids(from_member=from_member):
            res.append(
                self.get_member(cls_id)
            )
        return res

    def dispatch_parse(
            self,
            data: dict,
            dispatching_cls: Type[_DispatchingClsTV]
    ) -> _DispatchingClsTV:

        if dispatching_cls.get_cls_type() == "concrete":
            return dispatching_cls(**data)

        else:
            found_cls_id_maybe = data.get("class_id")
            if found_cls_id_maybe is None:
                raise ValueError(
                    f"dispatching class, '{dispatching_cls.get_class_id()}' is not concrete and "
                    f"we don't have a class_id specified"
                )

            found_cls_id = _cls_id_card.ClassId(found_cls_id_maybe)
            if not found_cls_id.startswith(dispatching_cls.get_class_id()):
                raise ValueError(
                    f"the dispatching class has class id '{dispatching_cls.get_class_id()}' "
                    f"and we found a class id, '{found_cls_id}' which is not a valid option."
                )

            concrete_cls = self.get_member(class_id=found_cls_id)
            if concrete_cls.get_cls_type() != "concrete":
                raise ValueError(
                    f"the found class id, '{found_cls_id}' maps to a non-concrete class"
                )
            return self.dispatch_parse(data=data, dispatching_cls=concrete_cls)


def _setup_dispatchable_class(
        cls: Type[DispatchableModelMixin],
        parent_cls_ix: int = 1,
) -> _cls_id_card.ClassIdCard:
    """
    hook that executes when creating the subclass. similar to metaclass mechanism
    """
    mro = cls.mro()
    direct_parent = mro[parent_cls_ix]
    if not issubclass(direct_parent, DispatchableModelMixin):
        raise ValueError(
            f"parent class, '{direct_parent.__name__}', "
            f"doesn't inherit from 'DispatchableModelMixin'"
        )

    class_name = cls.get_cls_name()

    # figure out the class type, then create the class id based on that
    class_id: _cls_id_card.ClassId
    class_type: _cls_id_card.ClassTypeT

    # determine the family tree based on the type of class
    family_head: Type[DispatchableModelMixin]

    # ### CLASS_TYPE INFERENCE ###

    # if this is inheriting directly from the mixin, we know it is a root
    if direct_parent == DispatchableModelMixin:
        class_type = "root"
        class_id = _cls_id_card.ClassId([class_name])

        # new family head
        family_head = cls

    # if direct parent is a subclass, but not the actual mixin class itself
    elif issubclass(direct_parent, DispatchableModelMixin):
        parent_id_card = direct_parent.get_class_id_card()
        parent_class_type = parent_id_card.cls_type

        # If class name begins with Abstract, we know it should be a passthrough, non-concrete.
        # We make sure the parent isn't concrete, bc we want to disallow concrete
        # classes from being subclasses
        if class_name.startswith("Abstract"):
            if parent_class_type in ["root", "passthrough"]:
                class_type = "passthrough"
            else:
                raise ValueError(
                    f"don't start class name with 'Abstract' and inherit from a concrete class"
                    f"parent class: {direct_parent}, this class: {cls}"
                )
        else:
            class_type = "concrete"

        class_id = parent_id_card.cls_id.joinpath(class_name)
        family_head = parent_id_card.family_head

    else:
        raise ValueError(
            f"parent class, '{direct_parent.__name__}', "
            f"doesn't inherit from 'DispatchableModelMixin'"
        )

    return _cls_id_card.ClassIdCard(
        cls_type=class_type,
        cls_id=class_id,
        family_head=family_head
    )
