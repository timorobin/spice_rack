from __future__ import annotations
from typing import Any, Optional
from typing_extensions import Self
from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic.generics import GenericModel

from spice_rack._base_classes._pydantic._common_methods_mixin import CommonMethods


__all__ = ("AbstractValueModel", "AbstractGenericValueModel")


class AbstractValueModel(BaseModel, CommonMethods):
    """
    This class doesn't define any attributes, it just enforces characteristics of a 'value'
    on subclasses of this class.

    main characteristics:

    1. These objects are frozen, i.e. you do not update an attribute on a given object,
        you create a new one
    2. Two value objects with the same attribute values are equal,
        i.e. their identity is determined by their values
    3. Value objects are not meant to be saved to the database on their,
        own they can be values on entity objects
    """
    class Config:
        frozen = True
        validate_assignment = True
        extra = "forbid"

    # model_config = ConfigDict(
    #     frozen=True,
    #     validate_assignment=True,
    #     extra="forbid",
    #     validate_default=True,
    # )

    def __eq__(self, other: AbstractValueModel) -> bool:
        if other.__class__ != self.__class__:
            return False
        self_data = self.dict()
        other_data = other.dict()
        return self_data == other_data

    @classmethod
    def update_forward_refs(cls, **kwargs: Any) -> None:
        imported_refs = cls._import_forward_refs()
        kwargs = {**imported_refs, **kwargs}
        return super().update_forward_refs(**kwargs)

    def _init_private_attributes(self) -> None:
        """
        Pydantic-provided hook that is called immediately after initialization.
        Unless a special situation, you should be overwriting our specified hooks rather than the
        pydantic one, so we're not tied to a pydantic api.

        Our hooks: "_post_init_setup" and "_post_init_validation"
        """
        super()._init_private_attributes()
        self._post_init_setup()
        self._post_init_validation()


class AbstractGenericValueModel(AbstractValueModel, GenericModel):
    """
    Combines pydantic's v1 GenericModel and our AbstractValueModel.
    Use this to create generic value model classes
    """

    @classmethod
    def validate(cls, value: Any, field: Optional[ModelField] = None) -> Self:
        # todo: explain why we do this
        if isinstance(value, AbstractGenericValueModel):
            if type(value).__parameters__:
                value = value.dict()
        return super().validate(value)
