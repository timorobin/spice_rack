from __future__ import annotations
from typing import Any, TypeVar, Generic

from abc import abstractmethod, ABC


__all__ = (
    "SpecialTypeMixin",
)


_CoercibleTV = TypeVar("_CoercibleTV", )
"""
use this type var to specify the type annotation for the raw data the given subclass is able to 
coerce into instances of the subclass. This is the type annotation on the arg in the '__new__' 
method for the below interface class.
"""


class SpecialTypeMixin(ABC, Generic[_CoercibleTV]):
    """
    This mixin provides common methods to all special type bases we define here.

    This standardizes how we handle initializing new instances and also ensures we hook into
    pydantic's validation engine correctly so the special type classes can be used
    as annotations for fields on pydantic models.
    """

    @abstractmethod
    def special_repr(self) -> str:
        """
        This keeps the regular '__repr__' method is the same as a standard lib data type
        this special type inherits from.
        """
        ...

    @classmethod
    @abstractmethod
    def _validate(cls, raw_data: _CoercibleTV) -> Any:
        """
        overwrite this classmethod to control how the raw data is
        validated and potentially mutated, before we create a new instance of this class
        """
        ...

    def __new__(cls, v: _CoercibleTV):
        """create a new instance of this special type class, validating the data first"""
        v = cls._validate(v)
        return super().__new__(cls, v)

    # # pydantic hooks

    # v1
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls

    # v2
    # Note: the commented out code doesn't account for the addition of the parameterization,
    #   but using the generic  setup should unlock the behavior we want,
    #   if we add some logic in a __class_getitem__ method

    # @classmethod
    # def __get_pydantic_core_schema__(
    #         cls,
    #         source_type: Any,
    #         handler: GetCoreSchemaHandler
    # ) -> core_schema.CoreSchema:
    #     schema = core_schema.no_info_before_validator_function(
    #         function=lambda raw_data: cls(raw_data), schema=core_schema.is_instance_schema(cls),
    #         serialization=core_schema.to_string_ser_schema(when_used="json-unless-none")
    #     )
    #     return schema
