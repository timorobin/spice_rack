from __future__ import annotations
import typing as t

import pydantic
import pydantic_core

__all__ = (
    "SpecialStrBase",
)


# coercible type annotation specifying you could also initialize this class with.
_CoercibleTV = t.TypeVar("_CoercibleTV", )
SelfTV = t.TypeVar("SelfTV", bound="SpecialStrBase")


class SpecialStrBase(str):
    """container for a special string to avoid having """

    @classmethod
    def _parse_non_str(cls, root_data: t.Any) -> str:
        """overwrite this to allow the special str class to parse non-string input"""
        raise TypeError(f"'{cls.__name__}' cannot parse data of type {type(root_data)}")

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        """overwrite this to specify the custom str formatting for this class"""
        return root_data

    @classmethod
    def _validate_str_val(cls, root_data: str) -> str:
        """validate that the formatted string data is valid"""
        return root_data

    @classmethod
    def _validate(cls, val: t.Any) -> str:
        str_val: str
        if not isinstance(val, str):
            str_val = cls._parse_non_str(val)
        else:
            str_val = val
        str_val = cls._format_str_val(str_val)
        return cls._validate_str_val(str_val)

    def __new__(cls, v: t.Union[str, _CoercibleTV]):
        """create a new instance of this special type class, validating the data first"""
        v = cls._validate(v)
        return super().__new__(cls, v)

    @classmethod
    def __get_pydantic_core_schema__(
            cls, _: t.Any, handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        final_schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=cls, schema=handler(str)
        )
        return final_schema

    def special_repr(self) -> str:
        """
        Gives us a special representation indicating the instance is a special string, not just
        a normal one.

        This keeps the regular '__repr__' method is the same as a normal str instance
        """
        return f"{self.__class__.__name__}['{str(self)}']"

    def __eq__(self: SelfTV, other: t.Union[SelfTV, str]) -> bool:
        other_formatted = self._validate(other)
        return str(self) == str(other_formatted)
