from __future__ import annotations
import typing as t
import enum
import types
import typing_extensions as t_ext
import pydantic
import pydantic_core
import inflection

from spice_rack._bases import _special_str
from spice_rack._bases import _base_base, _value_model


__all__ = (
    "DispatchedModelMixin",
    "ClassId",
    "DispatchedClassContainer",
    "DispatchableValueModelBase"
)


class ClassId(_special_str.SpecialStrBase):
    """the unique class id for a member of the dispatched family"""
    ...


ClassIdPathT = t.Tuple[ClassId, ...]


SelfTV = t.TypeVar("SelfTV", bound="DispatchedModelMixin")

_LiteralT: t_ext.TypeAlias = type(t.Literal["xxx"])  # type: ignore


class ClassType(enum.Enum):
    """
    the 'type' of class possible when within a family tree of DispatchedModelMixin
    """
    SUPER_ROOT = "super_root"
    """
    sits above the family tree we are creating. The entire 
    """

    ROOT = "root"
    """the first child of DispatchedModelMixin and potentially further roots."""

    CONCRETE = "concrete"
    """actual concrete type of the dispatched family tree. 
    You cannot inherit from this class it is Final
    """


# this has to be setup exactly as is. Anything overwriting __get_pydantic_core_schema__ will
# break the way we generate the pydantic core schema. I am not sure exactly why, but for now
# leave as is. This current setup does cause issues with pydantic_autodoc though.
class _ClassIdStr(str):
    ...
    # @classmethod
    # def __get_pydantic_core_schema__(
    #         cls, _: t.Any, __: pydantic.GetCoreSchemaHandler
    # ) -> pydantic_core.CoreSchema:
    #     return pydantic_core.core_schema.str_schema()


class _PydanticSchemaGenerator(pydantic.GenerateSchema):
    _specified_class_id: t.ClassVar[t.Optional[str]] = None

    def __class_getitem__(cls, item: ClassId) -> t.Type[_PydanticSchemaGenerator]:
        new_cls = types.new_class(f"{item}_schema_gen", bases=(cls, ))
        assert issubclass(new_cls, _PydanticSchemaGenerator), \
            f"{new_cls} not subclass of {_PydanticSchemaGenerator}?"
        new_cls._specified_class_id = str(item)
        return new_cls

    def match_type(self, obj: t.Type[t.Any]) -> pydantic_core.core_schema.CoreSchema:
        if obj is _ClassIdStr:
            return self.gen_class_id_schema()
        else:
            return super().match_type(obj)

    def gen_class_id_schema(self) -> pydantic_core.core_schema.CoreSchema:
        if self._specified_class_id is None:
            return pydantic_core.core_schema.str_schema()
        else:
            return pydantic_core.core_schema.with_default_schema(
                schema=pydantic_core.core_schema.literal_schema(
                    expected=[self._specified_class_id],
                ),
                default=self._specified_class_id
            )
        

_model_config = _base_base.BASE_MODEL_CONFIG
_model_config["schema_generator"] = _PydanticSchemaGenerator


class DispatchedModelMixin(_base_base.PydanticBase):
    """
    the entrypoint for creating dispatchable family trees using pydantic's internal
    engine for schema generation. Be careful not to inherit from two different
    dispatchable family trees at once. It will cause weird behavior and there
    are no checks to protect against this.

    """
    model_config = _model_config

    _class_type: t.ClassVar[ClassType] = ClassType.SUPER_ROOT
    _class_id: t.ClassVar[ClassId]
    _class_id_path: t.ClassVar[ClassIdPathT] = ()

    class_id: _ClassIdStr = pydantic.Field(
        description="this is the field we dispatch the different sub-classes on. "
                    "Concrete classes will constrain this to be only one specific value.",
        default=None,
    )

    @classmethod
    def _get_direct_parent(cls) -> t.Type[DispatchedModelMixin]:
        """iterate over MRO, find most recent DispatchedModelMixin subclass"""
        for _ancestor_cls in cls.mro()[1:]:
            if issubclass(_ancestor_cls, DispatchedModelMixin):
                return _ancestor_cls
        raise ValueError(
            "no subclass of 'DispatchedModelMixin' found?"
        )

    @classmethod
    def _infer_class_id(cls) -> ClassId:
        return ClassId(inflection.underscore(cls.__name__))

    @classmethod
    def _infer_class_type(cls) -> ClassType:
        parent_class = cls._get_direct_parent()
        parent_class_type = parent_class.get_class_type()

        # if super root parent, we assume root
        if parent_class_type == ClassType.SUPER_ROOT:
            class_type_actual = ClassType.ROOT

        # if root parent, we assume concrete
        elif parent_class_type == ClassType.ROOT:
            if cls.__name__.startswith("Abstract"):
                class_type_actual = ClassType.ROOT
            else:
                class_type_actual = ClassType.CONCRETE

        # if concrete parent, we raise ValueError
        elif parent_class_type == ClassType.CONCRETE:
            raise ValueError(
                f"'{cls.__name__}' direct parent is '{parent_class.__name__}' which is a"
                f" concrete class, so we shouldn't be inheriting from it."
            )
        else:
            raise ValueError(f"'{parent_class_type}' unexpected class type value")
        return class_type_actual

    def __init_subclass__(
            cls,
            class_type: t.Optional[t.Union[str, ClassType]] = None,
            class_id: t.Optional[t.Union[str, ClassType]] = None,
    ) -> None:
        """
        control how this subclass is set up.

        Args:
            class_type: specifies the class_id for the class. If specified, we'll use it
                otherwise it'll be constructed from the cls.__name__.
            class_id: If specified, we'll ensure it is valid based on the parent class' ClassType.
                See table below for more info

        Returns: None


        .. list-table:: Class Type specific behavior
           :widths: 100 25 25 25
           :header-rows: 1

           * - Class Type
             - Behavior
             - Possible Parents
             - Possible Children
           * - SUPER_ROOT
             - sits above the family tree. Subclass DispatchedModelMixin
                of the dispatching for entire trees.
             - SUPER_ROOT only
             - SUPER_ROOT or ROOT
           * - ROOT
             - means a class is not concrete, thus it cannot be instantiated directly
             - SUPER_ROOT or ROOT
             - ROOT or CONCRETE
           * - CONCRETE
             - means this is a "leaf" in the family tree. This class can be
                instantiated, and it should not be subclassed further.
             - ROOT only
             - None
        """

        class_id_actual: ClassId
        if class_id:
            class_id_actual = ClassId(class_id)
        else:
            class_id_actual = cls._infer_class_id()

        class_type_actual: ClassType
        if class_type:
            if isinstance(class_type, str):
                class_type_actual = ClassType(class_type.lower())
            else:
                class_type_actual = class_type
        else:
            class_type_actual = cls._infer_class_type()

        cls._class_id = class_id_actual
        cls._class_type = class_type_actual

        # if class_type_actual is CONCRETE, we adjust the schema gen stuff
        if class_type_actual == ClassType.CONCRETE:
            cls.model_config["schema_generator"] = _PydanticSchemaGenerator[cls._class_id]

        # if class_type is SUPER_ROOT, we initialize the class id path
        if class_type_actual == ClassType.SUPER_ROOT:
            cls._class_id_path = ()

        # if it is anything else, we set it using parent class' path
        else:
            parent_cls = cls._get_direct_parent()
            cls._class_id_path = parent_cls._class_id_path + (cls._class_id, )

    @classmethod
    def get_class_type(cls) -> ClassType:
        return cls._class_type

    @classmethod
    def get_class_id(cls) -> ClassId:
        return cls._class_id

    @classmethod
    def get_class_id_path(cls) -> ClassIdPathT:
        return cls._class_id_path

    @classmethod
    def is_concrete(cls) -> bool:
        return cls._class_type == ClassType.CONCRETE

    @classmethod
    def iter_concrete_subclasses(cls: t.Type[SelfTV]) -> t.Iterator[t.Type[SelfTV]]:
        if cls._class_type == ClassType.SUPER_ROOT:
            raise ValueError(
                f"don't call iter_concrete_subclasses on super root classes, "
                f"which '{cls.__name__}' is "
            )
        if cls.is_concrete():
            yield cls
        else:
            for sub_cls in cls.__subclasses__():
                for sub_sub_cls in sub_cls.iter_concrete_subclasses():
                    yield sub_sub_cls

    @pydantic.model_validator(mode="before")
    def _ensure_class_id(cls, data: t.Any) -> t.Any:
        if isinstance(data, dict):
            class_id_found = data.get("class_id")
            if not class_id_found:
                data["class_id"] = str(cls._class_id)
        return data

    @classmethod
    def model_validate(
        cls: t.Type[SelfTV],
        obj: t.Any,
        *args,
        **kwargs,
    ) -> SelfTV:
        if cls._class_type != ClassType.CONCRETE:
            raise ValueError(
                f"'{cls.__name__}' is not concrete, so we do not want"
                f" to initialize instances of this class"
            )
        else:
            return t.cast(SelfTV, super().model_validate(obj, *args, **kwargs))

    @classmethod
    def build_dispatched_ann(cls: t.Type[SelfTV]) -> t.Type[SelfTV]:
        """
        build a type annotation that is equivalent to Union[all concrete subclasses of this class]
        using class_id as a discriminator. This can be used as an annotation for a field in
        another pydantic class.
        """
        options = list(cls.iter_concrete_subclasses())

        if len(options) == 0:
            raise ValueError(
                f"'{cls.__name__}' has no concrete options"
            )
        if len(options) > 1:
            union_t = t.Union[tuple(options)]  # type: ignore
            annotated_t = t.Annotated[
                union_t,  # type: ignore
                pydantic.Discriminator("class_id")
            ]
            return annotated_t  # type: ignore
        else:
            return options[0]

    @classmethod
    def build_dispatcher_type_adapter(cls: t.Type[SelfTV]) -> pydantic.TypeAdapter[SelfTV]:
        """
        use the type annotation created by `build_dispatched_ann` in a pydantic TypeAdapter
        that allows us to get the "discriminated union" parsing functionality outside a
        pydantic class context. see pydantic type adapter docs
        """
        return pydantic.TypeAdapter(cls.build_dispatched_ann())

    @classmethod
    def get_all_concrete_subclass_ids(cls) -> t.List[ClassId]:
        res = []
        for concrete_sub_c in cls.iter_concrete_subclasses():
            res.append(
                concrete_sub_c.get_class_id()
            )
        return res


DispatchedClsTV = t.TypeVar("DispatchedClsTV", bound=DispatchedModelMixin)


class DispatchedClassContainer(pydantic.RootModel[DispatchedClsTV], t.Generic[DispatchedClsTV]):
    """
    convenience wrapper allowing you to specify a dispatched family root class as the class
    parameter, and it'll build the correct discriminated union type under the hood for you.
    """
    root: DispatchedClsTV = pydantic.Field(
        description="the underlying concrete class instance",
    )

    def __class_getitem__(
            cls,
            item: t.Type[DispatchedModelMixin]  # type: ignore
    ) -> t.Type[DispatchedClsTV]:
        if not issubclass(item, DispatchedModelMixin):
            raise ValueError(f"item must be subclass of DispatchedModelMixin, but {item} is not")
        return super().__class_getitem__(
            item.build_dispatched_ann()
        )  # type: ignore


class DispatchableValueModelBase(DispatchedModelMixin, class_type=ClassType.SUPER_ROOT):
    """
    convenience class that combines dispatchable model mixin and value model,
    which is a common use-case for dispatchable models. This has the value model config
    and the `DispatchedModelMixin` functionality.
    """
    model_config = _value_model.VALUE_MODEL_CONFIG
