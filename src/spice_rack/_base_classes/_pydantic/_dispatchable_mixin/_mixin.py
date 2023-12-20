from __future__ import annotations
from typing import ClassVar, Type, TypeVar, Optional, Iterator, Union, cast, Any
from pydantic import BaseModel, Field
from typing import Generic
from typing_extensions import Self
from enum import Enum

from spice_rack._base_classes._pydantic._dispatchable_mixin import _class_id_types


__all__ = (
    "DispatchableModelMixin",
)


class DispatchableModelMixin(BaseModel):
    """
    adds a class_id field and makes a registry for us to interact with.

    When making a new parent class, the leftmost parent class must be this class.
    """

    __family_tree__: ClassVar[_FamilyTree] = None
    __cls_type__: ClassVar[DispatchedChildClsTypeEnum] = None
    __cls_id_path__: ClassVar[_class_id_types.ClassIdPath] = None

    # would be a computed field in pydantic v2
    class_id: _class_id_types.ClassIdPath = Field(
        description="the class id path for this class, this is never set directly, only computed",
        default=None,
    )

    def __init_subclass__(
            cls,
            parent_cls_ix: int = 1,
            **kwargs
    ):
        _setup_dispatchable_class(
            cls=cls,
            parent_cls_ix=parent_cls_ix,
        )
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_family_tree(cls) -> _FamilyTree[_RootClsTV]:
        tree = cls.__family_tree__
        return tree

    @classmethod
    def build_concrete_union_type_ann(
            cls,
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

        if cls.__cls_type__ == DispatchedChildClsTypeEnum.CONCRETE:
            return cls
        else:
            concrete_subclasses = tuple(
                cls.get_family_tree().get_concrete_subclasses(from_member=cls)
            )

            union_type = Union[concrete_subclasses]
        res = cast(Type[Self], union_type)
        return res

    @classmethod
    def parse_obj(cls, obj: Any) -> Self:
        if cls.__cls_type__ == DispatchedChildClsTypeEnum.CONCRETE:
            return super().parse_obj(obj)
        else:
            if not isinstance(obj, dict):
                obj = dict(obj)

            return cls.get_family_tree().dispatch_parse(obj)


_RootClsTV = TypeVar(
    "_RootClsTV", bound=DispatchableModelMixin
)
DispatchingClsTV = TypeVar(
    "DispatchingClsTV", bound=DispatchableModelMixin
)


class _FamilyTree(Generic[_RootClsTV]):
    """holds family registry"""
    def __init__(
            self,
            root_cls: Type[_RootClsTV]
    ):
        if root_cls.__cls_type__ != DispatchedChildClsTypeEnum.ROOT:
            raise ValueError(f"cannot start a family tree with a non-root class. {root_cls}")

        self.root_cls = root_cls
        self._registry: dict[
            _class_id_types.ClassIdPath, Type[_RootClsTV]
        ] = {}

    def get_member(self, cls_id_path: _class_id_types.ClassIdPath) -> Type[_RootClsTV]:
        if cls_id_path not in self._registry:
            raise ValueError(
                f"'{cls_id_path}' not in the registry for the '{self.root_cls}' class"
            )

        else:
            return self._registry[cls_id_path]

    def add_member(self, new_member: Type[DispatchableModelMixin]) -> None:
        class_id_path = new_member.__cls_id_path__

        if class_id_path in self._registry:
            existing_cls = self.get_member(class_id_path)
            msg = (f"ClassIdPath collision:"
                   f" \n\tnew member: '{new_member}' \n\texisting class: '{existing_cls}'")
            raise ValueError(msg)

        else:
            self._registry[class_id_path] = new_member

    def iter_members(self) -> Iterator[Type[_RootClsTV]]:
        for member in self._registry.values():
            yield member

    def list_class_id_paths(
            self,
            from_member: Optional[Type[_RootClsTV]] = None,
            cls_types_only: Optional[list[DispatchedChildClsTypeEnum]] = None
    ) -> list[_class_id_types.ClassIdPath]:

        class_id_prefix: str
        if from_member is None:
            class_id_prefix = str(self.root_cls.class_id_path)
        else:
            class_id_prefix = str(from_member.class_id_path)

        if cls_types_only is None:
            cls_types_only = [
                DispatchedChildClsTypeEnum.ROOT,
                DispatchedChildClsTypeEnum.CONCRETE,
                DispatchedChildClsTypeEnum.PASSTHROUGH
            ]

        res: list[_class_id_types.ClassIdPath] = []
        for member_i in self.iter_members():
            if (
                    member_i.__cls_id_path__.startswith(class_id_prefix)
                    and
                    member_i.__cls_type__ in cls_types_only
            ):
                res.append(member_i.__cls_id_path__)
        return res

    def list_concrete_class_id_paths(
            self,
            from_member: Optional[Type[_RootClsTV]] = None,
    ) -> list[_class_id_types.ClassIdPath]:
        return self.list_class_id_paths(
            from_member=from_member, cls_types_only=[DispatchedChildClsTypeEnum.CONCRETE]
        )

    def get_concrete_subclasses(
            self,
            from_member: Optional[Type[_RootClsTV]] = None,
    ) -> list[Type[_RootClsTV]]:
        res = []
        for cls_id in self.list_concrete_class_id_paths(from_member=from_member):
            res.append(
                self.get_member(cls_id)
            )
        return res

    def dispatch_parse(
            self,
            data: dict,
            specified_dispatching_cls: Optional[Type[DispatchingClsTV]] = None
    ) -> DispatchingClsTV:

        concrete_cls: Type[DispatchingClsTV]
        dispatching_cls: Type[DispatchingClsTV]
        if specified_dispatching_cls is None:
            dispatching_cls = self.root_cls
        else:
            dispatching_cls = specified_dispatching_cls

        if dispatching_cls.__cls_type__ == DispatchedChildClsTypeEnum.CONCRETE:
            concrete_cls = dispatching_cls
        else:
            found_cls_id: _class_id_types.ClassIdPath = data.get("class_id")
            if found_cls_id is None:
                raise ValueError(
                    f"dispatching class, '{dispatching_cls.__cls_id_path__}' is not concrete and "
                    f"we don't have a class_id specified"
                )
            if not found_cls_id.startswith(dispatching_cls.__cls_id_path__):
                raise ValueError(
                    f"the dispatching class has class id '{dispatching_cls.__cls_id_path__}' "
                    f"and we found a class id, '{found_cls_id}' which is not a valid option."
                )

            concrete_cls = self.get_member(cls_id_path=found_cls_id)

        return concrete_cls.parse_obj(data)


class DispatchedChildClsTypeEnum(Enum):
    """valid args when subclasses dispatchable mixin"""
    # base means it is directly inheriting DispatchableMixin and should set up the family tree
    ROOT = "root"

    # this means the class is itself a base class, so shouldn't be initialized
    PASSTHROUGH = "passthrough"

    # this means the class is a concrete class and expects to be initialized
    CONCRETE = "concrete"


def _setup_dispatchable_class(
        cls: Type[DispatchableModelMixin],
        parent_cls_ix: int = 1,

) -> None:
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

    class_name = _class_id_types.ClassIdName(cls.__name__)

    class_id_path: _class_id_types.ClassIdPath
    cls_type: DispatchedChildClsTypeEnum

    # if this is inheriting directly from the mixin, we know it is a root
    if direct_parent == DispatchableModelMixin:
        cls_type = DispatchedChildClsTypeEnum.ROOT
        class_id_path = _class_id_types.ClassIdPath([class_name])

    # if direct parent is a subclass, but not the actual mixin class itself
    elif issubclass(direct_parent, DispatchableModelMixin):
        parent_cls_type = direct_parent.__cls_type__
        if parent_cls_type is None:
            raise ValueError(f"{direct_parent} doesn't have '__cls_type__' set?")

        # if class name begins with Abstract, we assume root

        if class_name.startswith("Abstract"):
            if parent_cls_type in (
                    DispatchedChildClsTypeEnum.ROOT,
                    DispatchedChildClsTypeEnum.PASSTHROUGH
            ):
                cls_type = DispatchedChildClsTypeEnum.PASSTHROUGH
            else:
                raise ValueError(
                    f"don't start class name with 'Abstract' and inherit from a concrete class"
                    f"parent class: {direct_parent}, this class: {cls}"
                )
        else:
            cls_type = DispatchedChildClsTypeEnum.CONCRETE

        class_id_path = direct_parent.__cls_id_path__.joinpath(class_name)
    else:
        raise ValueError(
            f"parent class, '{direct_parent.__name__}', "
            f"doesn't inherit from 'DispatchableModelMixin'"
        )

    cls.__cls_type__ = cls_type
    cls.__cls_id_path__ = class_id_path

    if cls_type == DispatchedChildClsTypeEnum.ROOT:
        cls.__family_tree__ = _FamilyTree(root_cls=cls)

    # update the default value for the class id path field, so it comes up on the schema gen
    class_id_field = cls.__fields__.get("class_id")

    # todo: const is removed in pydantic v2
    class_id_field.field_info.const = True
    class_id_field.default = class_id_path
    from typing import Literal
    dispatch_field.type_ = Literal[(cls.__class_id__,)]  # noqa - this is ok
