from __future__ import annotations
import typing as t
import typing_extensions as t_ext
import pydantic
import inflection

from spice_rack._bases import _special_str


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

_LiteralT: t_ext.TypeAlias = type(t.Literal["xxx"])
ClassMetaTypeT = t.Literal["root", "base", "concrete"]


class DispatchedModelMixin(pydantic.BaseModel, t.Generic[TypeTV]):
    """this creates a root of this dispatched class."""
    _cls_id: t.ClassVar[ClassId]
    _cls_meta_type: t.ClassVar[ClassMetaTypeT]
    _parent_cls_id_path: t.ClassVar[tuple[ClassId, ...]] = ()

    class_id: TypeTV = pydantic.Field(
        description="this will be overwritten in concrete classes to t.Literal['<cls_id_str>]', "
                    "and be str in base classes",
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
        if isinstance(params, t.TypeVar) or t.get_origin(params) == t.Literal:
            res = super().__class_getitem__(params)  # noqa

        else:

            cls_id = ClassId(params[0])
            cls_meta_type = params[1]

            cls_id_or_auto: t.Union[str, t.Literal["auto"]]
            cls_type_or_auto: t.Union[ClassMetaTypeT, t.Literal["auto"]]

            if cls_meta_type == "concrete":
                literal_t = t.Literal[(str(cls_id),)]  # noqa - this is ok
                res = super().__class_getitem__(literal_t)
                res.model_fields.get("class_id").default = str(cls_id)

            else:
                res = super().__class_getitem__(TypeTV)

            res._cls_id = cls_id
            res._cls_meta_type = cls_meta_type
            res._parent_cls_id_path += (cls._cls_id, )
        return res

    @classmethod
    def get_class_meta_type(cls) -> ClassMetaTypeT:
        return cls._cls_meta_type
    
    @classmethod
    def get_class_type(cls) -> str:
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
                f"don't call iter_concrete_subclasses on the DispatchedModelMixin class "
                f"itself, only on root classes built from it."
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
            return t.cast(SelfTV, super().model_validate(obj=obj, *args, **kwargs))

    @classmethod
    def build_dispatched_ann(cls: t.Type[SelfTV]) -> t.Type[SelfTV]:
        options = list(cls.iter_concrete_subclasses())

        if len(options) == 0:
            raise ValueError(
                f"'{cls.__name__}' has no concrete options"
            )
        if len(options) > 1:
            union_t = t.Union[tuple(options)]
            annotated_t = t.Annotated[
                union_t,
                pydantic.Discriminator("class_id")
            ]
            return annotated_t
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

    def __class_getitem__(cls, item: t.Type[DispatchedModelMixin]):
        if not issubclass(item, DispatchedModelMixin):
            raise ValueError(f"item must be subclass of DispatchedModelMixin, but {item} is not")
        return super().__class_getitem__(
            item.build_dispatched_ann()
        )
