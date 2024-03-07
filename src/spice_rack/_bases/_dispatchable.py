from __future__ import annotations
import typing as t
import enum
import typing_extensions as t_ext
import pydantic
import pydantic_core
import inflection

from spice_rack._bases import _special_str
from spice_rack._bases import _base_base


__all__ = (
    "DispatchedModelMixin",
    "ClassId",
    "DispatchedClassContainer"
)


class ClassId(_special_str.SpecialStrBase):
    """a class id for a member of the dispatched family"""

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        return inflection.underscore(root_data)


TypeTV = t.TypeVar("TypeTV", bound=ClassId)
SelfTV = t.TypeVar("SelfTV", bound="DispatchedModelMixin")

_LiteralT: t_ext.TypeAlias = type(t.Literal["xxx"])  # type: ignore


class ClassMetaTypeEnum(enum.Enum):
    """
    the 'type' of class possible when within a family tree of DispatchedModelMixin
    """
    SUPER_ROOT = "super_root"
    """only the actual 'DispatchedModelMixin' is this"""

    ROOT = "root"
    """the first child of DispatchedModelMixin and potentially further roots."""

    CONCRETE = "concrete"
    """actual concrete type of the dispatched family tree. 
    You cannot inherit from this class it is Final
    """


class _ClassIdStr(str):
    ...


class _PydanticSchemaGenerator(pydantic.GenerateSchema):
    _specified_class_id: t.ClassVar[t.Optional[str]] = None

    def __init_subclass__(cls, class_id: t.Optional[str] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._specified_class_id = class_id

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


class DispatchedModelMixin(pydantic.BaseModel, _base_base.CommonModelMethods):
    """
    this creates a root of this dispatched class.

    see '__init_subclass__' for how to specify subclasses and control class setup

    """
    model_config = _model_config

    _cls_id: t.ClassVar[ClassId]
    _cls_meta_type: t.ClassVar[ClassMetaTypeEnum] = ClassMetaTypeEnum.SUPER_ROOT

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
            f"no subclass of 'DispatchedModelMixin' found?"
        )

    def __init_subclass__(
            cls,
            dispatch_param: t.Union[
                str,
                ClassMetaTypeEnum,
                None,
            ] = None
    ) -> None:
        """
        control how this subclass is set up

        Args:
            dispatch_param:
                str: we treat as class_id
                ClassMetaTypeEnum: we treat as class_meta_type being manually specified
                None: we infer this class to be a root.

        Returns:
            Nothing: just setups up the class
        """

        # determine class_meta_type
        concrete_class_id: t.Optional[str] = None
        class_meta_type: ClassMetaTypeEnum
        if dispatch_param is None:
            class_meta_type = ClassMetaTypeEnum.ROOT

        elif isinstance(dispatch_param, ClassMetaTypeEnum):
            class_meta_type = dispatch_param

        elif isinstance(dispatch_param, str):
            concrete_class_id = dispatch_param
            class_meta_type = ClassMetaTypeEnum.CONCRETE

        else:
            raise ValueError(f"unexpected dispatch_param val: {dispatch_param}'")

        parent_cls = cls._get_direct_parent()
        # make sure the most recent parent is root, this is no matter what type of class this is
        if parent_cls.get_class_meta_type() == ClassMetaTypeEnum.CONCRETE:
            raise ValueError(
                f"'{cls.__name__}' is trying to subclass a concrete class, "
                f"'{parent_cls.__name__}'"
            )

        cls._cls_meta_type = class_meta_type

        # make sure the two are valid together
        if class_meta_type == ClassMetaTypeEnum.CONCRETE:
            if concrete_class_id is None:
                raise ValueError(
                    f"'{cls.__name__}' didn't specify their concrete_class_id and "
                    f"and be a non-concrete metatype"
                )
            class_id = ClassId(concrete_class_id)
            cls._cls_id = class_id

            class _CustomSchemaGen(_PydanticSchemaGenerator, class_id=str(cls._cls_id)):
                ...
            cls.model_config["schema_generator"] = _CustomSchemaGen

    @classmethod
    def get_class_meta_type(cls) -> ClassMetaTypeEnum:
        return cls._cls_meta_type

    @classmethod
    def is_concrete(cls) -> bool:
        return cls._cls_meta_type == ClassMetaTypeEnum.CONCRETE

    @classmethod
    def iter_concrete_subclasses(cls: t.Type[SelfTV]) -> t.Iterator[t.Type[SelfTV]]:
        if cls._cls_meta_type == ClassMetaTypeEnum.SUPER_ROOT:
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
                data["class_id"] = str(cls._cls_id)
        return data

    @classmethod
    def model_validate(
        cls: t.Type[SelfTV],
        obj: t.Any,
        *args,
        **kwargs,
    ) -> SelfTV:
        if cls._cls_meta_type != ClassMetaTypeEnum.CONCRETE:
            raise ValueError(
                f"'{cls.__name__}' is not concrete, so we do not want"
                f" to initialize instances of this class"
            )
        else:
            return t.cast(SelfTV, super().model_validate(obj, *args, **kwargs))

    @classmethod
    def build_dispatched_ann(cls: t.Type[SelfTV]) -> t.Type[SelfTV]:
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
        return pydantic.TypeAdapter(cls.build_dispatched_ann())


DispatchedClsTV = t.TypeVar("DispatchedClsTV", bound=DispatchedModelMixin)


class DispatchedClassContainer(pydantic.RootModel[DispatchedClsTV], t.Generic[DispatchedClsTV]):
    root: DispatchedClsTV = pydantic.Field(
        description="the root class ",
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
