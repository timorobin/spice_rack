from __future__ import annotations
from typing import Any, Union  # , TypeVar, Generic
from abc import abstractmethod

from spice_rack._base_classes._special_types._special_type_mixin import SpecialTypeMixin

__all__ = (
    "AbstractSpecialStr",
)


# _SpecialStrCoercibleTV = TypeVar("_SpecialStrCoercibleTV", )
# """
# Carried over the generic param from the SpecialTypeMixin class. Specify the type parameter
# when subclassing to indicate the types we can coerce to the subclass type, i.e. any
# non-str data types supported because str is always supported
# """

# this second-level generic param broke stuff not sure why
_SpecialStrCoercibleTV = Any


class AbstractSpecialStr(
    SpecialTypeMixin[Union[str, _SpecialStrCoercibleTV]],
    # Generic[_SpecialStrCoercibleTV],
    str
):
    """
    Subclass of string indicating a constrained version of a string.

    Notes:
        - This has the correct methods defined to hook into pydantic validation when used as
          an annotation for a pydantic field.
        - All comparisons still work as normal string to string comparisons as default behavior,
          but this can be modified in subclasses
    """

    def special_repr(self) -> str:
        """
        Gives us a special representation indicating the instance is a special string, not just
        a normal one.

        This keeps the regular '__repr__' method is the same as a normal str instance
        """
        return f"{self.__class__.__name__}['{self}']"

    @classmethod
    @abstractmethod
    def _format_str(cls, root_data: str) -> str:
        """overwrite this to specify the custom str formatting for this class"""
        ...

    @classmethod
    def _parse_non_str(cls, root_data: Any) -> str:
        """overwrite this to allow the special str class to parse non-string input"""
        raise TypeError(f"'{cls.__name__}' cannot parse data of type {type(root_data)}")

    @classmethod
    def _validate(cls, raw_data: Union[str, _SpecialStrCoercibleTV]) -> str:
        """perform validation on the raw data before creating a new instance."""
        if not isinstance(raw_data, str):
            str_data = cls._parse_non_str(root_data=raw_data)
        else:
            str_data = raw_data

        return cls._format_str(root_data=str_data)

    # # v2 stuff
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
