from __future__ import annotations
from typing import ClassVar, Type, Iterator, Any, Sequence, Literal, TYPE_CHECKING
from pydantic import BaseModel, Field, validator
from typing_extensions import TypeAlias

from spice_rack._base_classes import _special_types
from spice_rack._base_classes._pydantic import _misc

if TYPE_CHECKING:
    from spice_rack._base_classes._pydantic._dispatchable_mixin import _mixin
    RootClsT: TypeAlias = Type[_mixin.DispatchableModelMixin]


__all__ = (
    "ClassId",
    "ClassTypeT",
    "ClassIdCard",
)


class ClassId(
    # generic param removed for now, see the module for the issues
    # _special_types.special_str_base.AbstractSpecialStr[Sequence[str]]
    _special_types.special_str_base.AbstractSpecialStr
):
    """a path of class names connected with a separator"""
    _sep: ClassVar[str] = "."

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data

    @classmethod
    def _parse_non_str(cls, root_data: Any) -> str:
        if isinstance(root_data, Sequence):
            pieces: list[_misc.ClassName] = [_misc.ClassName(part) for part in root_data]
            single_str = cls._sep.join(pieces)
            return single_str
        else:
            return super()._parse_non_str(root_data)

    def iter_parts(self) -> Iterator[_misc.ClassName]:
        for part in self.split(self._sep):
            yield _misc.ClassName(part)

    def joinpath(self, class_name: _misc.ClassName) -> ClassId:
        parts = list(self.iter_parts())
        parts.append(class_name)
        return ClassId(parts)


ClassTypeT = Literal["root", "passthrough", "concrete"]


class ClassIdCard(BaseModel):
    """
    Info about the class such as family tree, class type and its ID.
    """
    class Config:
        frozen = True
        validate_assignment = True
        extra = "forbid"

    cls_id: ClassId = Field(
        description="ID for this class, unique within its family tree"
    )

    cls_type: ClassTypeT = Field(
        description="the type of class this is, root, passthrough or concrete"
    )

    family_head: RootClsT = Field(
        description="The root class of the family tree this class is apart of. "
                    "we can access this class' family tree via this class"
    )

    @validator("family_head", pre=False, )
    def _check_cls_type(cls, v: RootClsT) -> RootClsT:
        # todo: check that it is cls_type == "root"
        return v

    @classmethod
    def update_forward_refs(cls, **kwargs) -> None:
        from spice_rack._base_classes._pydantic._dispatchable_mixin import _mixin
        kwargs["RootClsT"] = Type[_mixin.DispatchableModelMixin]
        super().update_forward_refs(**kwargs)
