from __future__ import annotations
import typing as t
from pydantic import Field

from spice_rack._bases._value_model import ValueModelBase


__all__ = (
    "ErrorInfoBase",
    "ErrorPayload"
)


class ErrorInfoBase(ValueModelBase):
    """base object that holds information about a specific error."""
    extra: dict = Field(
        description="dict field where you can add extra info. "
                    "Can include any data types but everything must be json serializable",
        default_factory=dict
    )

    def get_json_data(self, **pydantic_kwargs) -> dict:
        return self.json_dict(use_str_fallback=True, **pydantic_kwargs)


ErrorInfoTV = t.TypeVar("ErrorInfoTV", bound=ErrorInfoBase)


class ErrorPayload(ValueModelBase, t.Generic[ErrorInfoTV]):
    """
    Generic payload class holding the error detail string, and the info object.
    The ErrorInfoTV type var dictates the unique
    schema information about the concrete class
    """
    _custom_schema_title: t.ClassVar[t.Optional[str]] = None
    detail: str = Field(description="the top line error")

    error_type: str = Field(
        description="the name of the error class this payload is connected to"
    )
    info: ErrorInfoTV = Field(
        description="object containing more detailed information about the error"
    )
