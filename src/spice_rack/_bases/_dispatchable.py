from __future__ import annotations
import typing as t

import typing_extensions as t_ext
import pydantic
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

ClassMetaTypeT = t.Literal["root", "base", "concrete"]


def _json_schema_extra(schema: dict) -> None:
    """remove default from class id field and add it to the required fields"""
    schema["properties"]["class_id"].pop("default", None)
    required_fields = schema.get("required", [])
    if "class_id" not in required_fields:
        required_fields = ["class_id", *required_fields]
    schema["required"] = required_fields


_model_config = _base_base.BASE_MODEL_CONFIG
_model_config["json_schema_extra"] = _json_schema_extra


class DispatchedModelMixin(pydantic.BaseModel, _base_base.CommonModelMethods, t.Generic[TypeTV]):
    """this creates a root of this dispatched class."""
    model_config = _model_config

    _cls_id: t.ClassVar[ClassId]
    _cls_meta_type: t.ClassVar[ClassMetaTypeT]
    _parent_cls_id_path: t.ClassVar[tuple[ClassId, ...]] = ()

    class_id: TypeTV = pydantic.Field(
        description="this will be overwritten in concrete classes to t.Literal['<cls_id_str>]', "
                    "and be str in base classes",
        default=None,
    )

    @classmethod
    def model_parametrized_name(cls, params: tuple[type[t.Any], ...]) -> str:
        res = super().model_parametrized_name(params)
        return f"_ParameterizedPassthrough{res}"

    def __class_getitem__(
            cls: t.Type[SelfTV],
            params: t.Union[
                t.TypeVar,
                _LiteralT,
                t.Tuple[
                    str,
                    ClassMetaTypeT,
                ]
            ]
    ) -> t.Type[SelfTV]:
        """
        the bracket style subclassing

        Args:
            params: todo: doc each type of arg

        Returns:
            a newly built class
        """
        res: t.Type[SelfTV]

        # this is the base situation so keep passing back
        if t.get_origin(params) == t.Literal:
            res = super().__class_getitem__(params)  # type: ignore

        # this is a root class, i.e. it a new parent
        elif isinstance(params, t.TypeVar):
            res = super().__class_getitem__(params)  # type: ignore
            res._cls_id = ClassId(res.__name__)

        else:
            cls_id = ClassId(params[0])
            cls_meta_type = params[1]
            if cls_meta_type == "concrete":
                literal_t = t.Literal[(str(cls_id),)]  # type: ignore
                res = super().__class_getitem__(literal_t)  # type: ignore
                model_field = res.model_fields["class_id"]
                model_field.default = str(cls_id)

            else:
                res = super().__class_getitem__(TypeTV)  # type: ignore

            res._cls_id = cls_id
            res._cls_meta_type = cls_meta_type
            res._parent_cls_id_path += (ClassId(cls.get_class_type()), )
        return res

    @classmethod
    def get_class_meta_type(cls) -> ClassMetaTypeT:
        return cls._cls_meta_type
    
    @classmethod
    def get_class_type(cls) -> str:
        if not hasattr(cls, "_cls_id"):
            raise ValueError(
                f"'{cls.__name__}' didn't set their '_cls_id' class attribute"
            )
        else:
            return str(cls._cls_id)

    @classmethod
    def _is_parameterized_passthrough(cls) -> bool:
        return cls.__name__.startswith("_ParameterizedPassthrough")

    @classmethod
    def is_concrete(cls) -> bool:
        return cls._cls_meta_type == "concrete" and not cls._is_parameterized_passthrough()

    @classmethod
    def iter_concrete_subclasses(cls: t.Type[SelfTV]) -> t.Iterator[t.Type[SelfTV]]:
        if cls.__name__ == DispatchedModelMixin.__name__:
            raise ValueError(
                "don't call iter_concrete_subclasses on the DispatchedModelMixin class "
                "itself, only on root classes built from it."
            )
        if cls.is_concrete():
            yield cls
        else:
            for sub_cls in cls.__subclasses__():
                for sub_sub_cls in sub_cls.iter_concrete_subclasses():
                    yield sub_sub_cls

    @classmethod
    def model_validate(
        cls: t.Type[SelfTV],
        obj: t.Any,
        *args,
        **kwargs,
    ) -> SelfTV:
        if cls._cls_meta_type != "concrete":
            raise ValueError(
                f"'{cls.get_class_type()}' is not concrete, so we do not want"
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
