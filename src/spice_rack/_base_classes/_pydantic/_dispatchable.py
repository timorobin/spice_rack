from __future__ import annotations
import typing as t
from abc import abstractmethod
from typing import Any

from pydantic import Field, validator
from pydantic.generics import GenericModel
from pydantic.fields import ModelField

from spice_rack._base_classes import _enums


__all__ = (
    "ConcreteClassIdEnumBase",
    "DispatchableModelMixin"
)


_CLASS_ID_FIELD = "class_id"


class ConcreteClassIdEnumBase(_enums.StrEnum):
    """
    base class for an enum of types you must create when creating a dispatchable family
    of classes. Each entry here must correspond to a concrete child class within a given
    dispatchable class' tree.
    """
    ...


_ClassIdEnumTV = t.TypeVar("_ClassIdEnumTV", bound=ConcreteClassIdEnumBase)

# PyCharm IDE works if we do this rather than Self
Self = t.TypeVar("Self", bound="DispatchableModelMixin")


class DispatchableModelMixin(GenericModel, t.Generic[_ClassIdEnumTV]):
    """
    infuses class_id field and the relevant functionality to automatically
    dispatch to the correct concrete class.

    if you are making a new root, specifying is_new_root=True in the
    subclass kwargs.

    If concrete, specify is_concrete=True.
    """
    _cls_id_enum_cls: t.Type[_ClassIdEnumTV]
    _root_cls: t.Type[DispatchableModelMixin] = None
    _root_cls_registry: ConcreteClsRegistry = None

    # make sure this attr name equals _CLASS_ID_FIELD global
    class_id: str = Field(
        description="the class id attribute, we assign the default always.",
        default="placeholder"
    )

    @validator("class_id", pre=True, always=True)
    def _handle_enum_member(cls, v):
        if isinstance(v, ConcreteClassIdEnumBase):
            v = v.value

        else:
            class_id = cls.get_cls_id_str()
            if v != class_id:
                raise ValueError(
                    f"'{v}' is not the correct class id for {cls}. expected {class_id}"
                )

        return v

    def __class_getitem__(
            cls,
            item: t.Type[_ClassIdEnumTV]
    ) -> t.Type[DispatchableModelMixin]:
        new_cls = super().__class_getitem__(item)  # noqa - Generic should give us this
        new_cls._cls_id_enum_cls = item
        return new_cls

    @classmethod
    @abstractmethod
    def get_cls_id(cls) -> t.Optional[_ClassIdEnumTV]:
        """
        define your own enum, and for every concrete class, add an entry and return it here.
        must be 1 to 1. If this returns None, we assume it is a passthrough, i.e. non-concrete
        non-root class.
        """
        ...

    @classmethod
    def get_cls_id_str(cls) -> t.Optional[str]:
        cls_id_maybe = cls.get_cls_id()
        if cls_id_maybe:
            return cls_id_maybe.value
        else:
            return None

    @classmethod
    def get_cls_registry(cls: t.Type[Self]) -> ConcreteClsRegistry[_ClassIdEnumTV, Self]:
        return cls._root_cls_registry.get_narrowed_registry(cls)

    @classmethod
    def is_concrete(cls) -> bool:
        return cls.get_cls_id() is not None

    @classmethod
    def _setup_subclass(cls, is_concrete: bool, is_new_root: bool) -> None:
        """
        Mutates the cls upon subclass. Essentially the '__init_subclass__' hook.

        Notes:
            In pydantic v1 this is called in the standard lib hook '__init_subclass__'
            but in pydantic v2 there is an exposed hook to call it after init subclass, which
            would be a better implementation for this situation. Implemented this logic
            in its own classmethod to make that move easier.
        """
        if is_new_root:
            cls._root_cls = cls
            cls._root_cls_registry = ConcreteClsRegistry[cls._cls_id_enum_cls, cls](__root__={})
            if is_concrete:
                raise ValueError(f"{cls} cannot be both new root and concrete")

        if is_concrete:
            if cls._root_cls_registry is None:
                raise ValueError(
                    f"{cls} is concrete but no concrete class registry set"
                )

            class_id_maybe = cls.get_cls_id()
            if class_id_maybe:
                class_id_str = class_id_maybe.value

                # we know this is concrete
                class_id_field: ModelField = cls.__fields__.get(_CLASS_ID_FIELD)

                # v1 only, const will be determined by literal of one choice automatically in v2
                class_id_field.field_info.const = True

                # always set
                class_id_field.default = class_id_str

                # we want Literal so we can use discriminated union
                from typing import Literal
                class_id_field.type_ = Literal[(class_id_str, )]  # noqa - this is ok

                cls._root_cls_registry.add_member(cls)

            else:
                raise ValueError(f"{cls} is concrete but 'get_cls_id' returned None")

    def __init_subclass__(
            cls,
            is_new_root: bool = False,
            is_concrete: bool = False,
            **kwargs
    ):
        super().__init_subclass__()
        cls._setup_subclass(
            is_concrete=is_concrete,
            is_new_root=is_new_root,
        )

    @classmethod
    def get_concrete_cls_registry(
            cls: t.Type[Self]
    ) -> ConcreteClsRegistry[_ClassIdEnumTV, Self]:
        return cls._root_cls_registry.get_narrowed_registry(cls)

    @classmethod
    def iter_concrete_subclasses(cls: t.Type[Self]) -> t.Iterator[t.Type[Self]]:
        for sub_class in cls.get_cls_registry().iter_classes():
            yield sub_class

    @classmethod
    def get_concrete_cls(
            cls: t.Type[Self],
            class_id_or_str: t.Union[str, _ClassIdEnumTV]
    ) -> t.Type[Self]:
        class_id: _ClassIdEnumTV
        if isinstance(class_id_or_str, str):
            try:
                class_id = cls._cls_id_enum_cls(class_id_or_str)
            except Exception as e:
                raise ValueError(
                    f"the value specified for the '{_CLASS_ID_FIELD}' field was "
                    f"'{class_id_or_str}' which isn't valid for the enum class, "
                    f"'{cls._cls_id_enum_cls}'"
                ) from e
        else:
            class_id = class_id_or_str

        if cls.get_cls_id():
            if class_id != cls.get_cls_id():
                raise ValueError(
                    f"{cls} doesn't haven't a concrete subclass with id {class_id}"
                )
            else:
                return cls
        else:

            for sub_cls in cls.iter_concrete_subclasses():
                if sub_cls.get_cls_id() == class_id:
                    return sub_cls
            raise ValueError(
                f"{cls} doesn't haven't a concrete subclass with id {class_id}"
            )

    @classmethod
    def _dispatch_parse(cls: t.Type[Self], data: dict) -> Self:
        if cls.is_concrete():

            # we know concrete so just call regular init
            return cls(**data)

        else:
            # we need to dispatch
            found_cls_id_raw_maybe = data.get(_CLASS_ID_FIELD)
            if found_cls_id_raw_maybe:
                sub_cls = cls.get_concrete_cls(class_id_or_str=found_cls_id_raw_maybe)
                return sub_cls(**data)

            else:
                from devtools import debug
                debug(data)
                raise ValueError(
                    f"must specify a '{_CLASS_ID_FIELD}' value to parse"
                    f" an object using this class, {cls.__name__}"
                )

    @classmethod
    def parse_obj(cls: t.Type[Self], obj: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        else:
            data: dict
            if not isinstance(obj, dict):
                try:
                    data = dict(obj)
                except Exception as e:
                    raise ValueError(
                        f"unable to convert obj of type {type(obj)} to a dict."
                    ) from e
            else:
                data = obj
            return cls._dispatch_parse(data)

    @classmethod
    def validate(cls: t.Type[Self], value: Any) -> Self:
        if isinstance(value, cls):
            return value
        else:
            data: dict
            if not isinstance(value, dict):
                try:
                    data = dict(value)
                except Exception as e:
                    raise ValueError(
                        f"unable to convert obj of type {type(value)} to a dict."
                    ) from e
            else:
                data = value

            return cls._dispatch_parse(data)

    @classmethod
    def build_union_type(cls: t.Type[Self]) -> t.Type[Self]:
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
        union_type = cls.get_cls_registry().build_concrete_union_ann()
        return t.cast(
            cls, union_type
        )


_RootClsTV = t.TypeVar("_RootClsTV", bound=DispatchableModelMixin)
_NarrowedClsTV = t.TypeVar("_NarrowedClsTV", bound=DispatchableModelMixin)


class ConcreteClsRegistry(GenericModel, t.Generic[_ClassIdEnumTV, _RootClsTV]):
    _enum_cls: t.ClassVar[t.Type[ConcreteClassIdEnumBase]]
    _root_cls: t.ClassVar[t.Type[DispatchableModelMixin]]

    __root__: dict[_ClassIdEnumTV, _RootClsTV] = Field(description="the registry")

    def __class_getitem__(
            cls, item: tuple[t.Type[ConcreteClassIdEnumBase], t.Type[DispatchableModelMixin]]
    ) -> t.Type[ConcreteClsRegistry]:
        new_cls: t.Type[ConcreteClsRegistry] = super().__class_getitem__(item)
        new_cls._enum_cls = item[0]
        new_cls._root_cls = item[1]
        return new_cls

    def add_member(self, new_member: t.Type[_RootClsTV]) -> None:
        cls_id: _ClassIdEnumTV
        cls_id_maybe = new_member.get_cls_id()
        if cls_id_maybe:
            if not isinstance(cls_id_maybe, self._enum_cls):
                raise ValueError(
                    f"expected class id to be type {self._enum_cls}, "
                    f"encountered {type(cls_id_maybe)}"
                )
            else:
                cls_id = cls_id_maybe
        else:
            raise ValueError(
                f"{new_member} doesn't have a class id so it isn't concrete"
            )

        if cls_id in self.__root__:
            raise ValueError(
                f"'{cls_id}' already exists in the registry."
            )
        else:
            self.__root__[cls_id] = new_member

    def lookup_member(
            self,
            class_id_or_str: t.Union[str, _ClassIdEnumTV]
    ) -> t.Type[_RootClsTV]:
        class_id: _ClassIdEnumTV
        if isinstance(class_id_or_str, str):
            try:
                class_id = self._enum_cls(class_id_or_str)
            except Exception as e:
                raise ValueError(
                    f"the value specified for the '{_CLASS_ID_FIELD}' field was "
                    f"'{class_id_or_str}' which isn't valid for the enum class, "
                    f"'{self._enum_cls}'"
                ) from e
        else:
            class_id = class_id_or_str

        cls_maybe = self.__root__.get(class_id)
        if cls_maybe is None:
            raise ValueError(
                f"{self._root_cls} doesn't haven't a concrete subclass with id {class_id}"
            )
        else:
            return cls_maybe

    def get_narrowed_registry(
            self,
            passthrough_cls: t.Type[_NarrowedClsTV]
    ) -> ConcreteClsRegistry[_ClassIdEnumTV, _NarrowedClsTV]:

        new_registry = ConcreteClsRegistry[self._enum_cls, passthrough_cls](__root__={})

        for key, cls in self.__root__.items():
            if issubclass(cls, passthrough_cls):
                new_registry.add_member(cls)
        return new_registry

    def iter_classes(self) -> t.Iterator[t.Type[_RootClsTV]]:
        for subclass in self.__root__.values():
            yield subclass

    def build_concrete_union_ann(self) -> Any:
        options = tuple(self.iter_classes())
        union_type = t.Union[options]
        return union_type
