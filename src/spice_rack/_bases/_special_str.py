from __future__ import annotations
import typing as t
from copy import copy

import pydantic
import pydantic_core

__all__ = (
    "SpecialStrBase",
    "StrKeyBase"
)


# coercible type annotation specifying you could also initialize this class with.
_CoercibleTV = t.TypeVar("_CoercibleTV", )
SelfTV = t.TypeVar("SelfTV", bound="SpecialStrBase")


class SpecialStrBase(str):
    """
    makes it convenient to subclass str to let us signify a given str is a special
    type, like an ID or key. This helps type checking and also allows us to add formatting and
    validation. This class also hooks into pydantic validation automatically.
    """
    @classmethod
    def _parse_non_str(cls, root_data: t.Any) -> str:
        """
        Overwrite this to allow the special str class to parse non-string input.
        Manually check the root_data type to determine if you want to parse, it and return
        super()._parse_non_str if you want to avoid handling the data type.
        """
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

    def __eq__(self: SelfTV, __value: object) -> bool:
        try:
            other_formatted = self._validate(__value)
            return str(self) == str(other_formatted)

        except Exception:
            return False

    def __hash__(self) -> int:
        return hash(str(self))


class StrKeyBase(SpecialStrBase):
    """
    extension on 'AbstractSpecialStr' to easily make a new special str class we intend
    to use as some sort of key. The main functionality is when you want to standardize a str value
    as either upper or lower case, and replace common separators with a standard one.
    """
    @classmethod
    def _get_separator(cls) -> str:
        """the standard separator we want to use for the key. overwrite this to customize it"""
        return "_"

    @classmethod
    def _get_separators_to_replace(cls) -> list[str]:
        """
        a list of common separators we want to replace with the standard separator.
        overwrite this to customize the list.
        """
        return [" ", "_", ".", "-"]

    @classmethod
    def _get_case_formatting(cls) -> _CaseFormattingT:
        """
        determine how to handle the case of the string.

        Returns:
            "upper": cast str to all uppercase
            "lower" cast str to all lowercase
            "as_is": leave string unchanged
        """
        return "as_is"

    @classmethod
    def _apply_case_formatting(cls, s: str) -> str:
        option = cls._get_case_formatting()
        if option == "as_is":
            return s
        elif option == "lower":
            return s.lower()
        elif option == "upper":
            return s.upper()
        else:
            raise ValueError(
                f"'{option}' is not a valid choice for the case formatter"
            )

    @classmethod
    def _format_str_val(cls, root_data: str) -> str:
        # replace separators
        formatted_str = copy(root_data)

        good_sep = cls._get_separator()
        seps_to_replace = [sep for sep in cls._get_separators_to_replace() if sep != good_sep]
        for bad_sep in seps_to_replace:
            formatted_str = formatted_str.replace(bad_sep, good_sep)

        return cls._apply_case_formatting(formatted_str)


_CaseFormattingT = t.Literal["upper", "lower", "as_is"]
