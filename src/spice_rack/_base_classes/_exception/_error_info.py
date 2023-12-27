from __future__ import annotations
from typing import Generic, TypeVar, Optional, Type, ClassVar, Any
from pydantic import Field

from spice_rack._base_classes import _pydantic as pydantic_bases

__all__ = (
    "ErrorInfoBase",
    "ErrorPayload"
)


def _exception_json_encoder(exception_inst: Exception) -> ErrorPayload:
    """
    ensures all exceptions are dumped to our payload format.
    """
    from spice_rack._base_classes._exception._exception_base import CustomExceptionBase

    # if one of ours, we use the formatting functionality
    if isinstance(exception_inst, CustomExceptionBase):
        return exception_inst.get_error_payload_inst()

    else:
        return ErrorPayload[ErrorInfoBase](
            detail=str(exception_inst),
            error_type=type(exception_inst).__name__,
            info=ErrorInfoBase(),
        )


class ErrorInfoBase(pydantic_bases.AbstractValueModel):
    """base object that holds information about a specific error."""
    extra: dict = Field(
        description="dict field where you can add extra info. "
                    "Can include any data types but everything must be json serializable",
        default_factory=dict
    )

    def get_json_data(self, **pydantic_kwargs) -> dict:
        return self.json_dict(use_str_fallback=True, **pydantic_kwargs)


ErrorInfoTV = TypeVar("ErrorInfoTV", bound=ErrorInfoBase)


class ErrorPayload(pydantic_bases.AbstractGenericValueModel, Generic[ErrorInfoTV]):
    """
    Generic payload class holding the error detail string, and the info object.
    The ErrorInfoTV type var dictates the unique
    schema information about the concrete class
    """
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Exception: _exception_json_encoder,
            type: lambda x: str(x)
        }

        @staticmethod
        def schema_extra(schema: dict[str, Any], model: Type[ErrorPayload]) -> None:
            """
            see: https://docs.pydantic.dev/1.10/usage/schema/#schema-customization

            Args:
                schema: schema we're mutating
                model: this class

            Returns: nothing, it mutates in place
            """
            schema["title"] = model.get_schema_title()

    _custom_schema_title: ClassVar[Optional[str]] = None

    detail: str = Field(description="the top line error")
    error_type: str = Field(
        description="the name of the error class this payload is connected to"
    )
    info: ErrorInfoTV = Field(
        description="object containing more detailed information about the error"
    )
    extra: Optional[dict] = Field(
        description="don't use this field, it shouldn't be part of this model",
        default=None, const=True, exclude=True
    )

    @classmethod
    def set_schema_title(cls, custom_title: str) -> None:
        cls._custom_schema_title = custom_title

    @classmethod
    def get_schema_title(cls) -> str:
        """gets either the custom schema title we've set or the class name"""
        if cls._custom_schema_title:
            return cls._custom_schema_title
        else:
            return cls.__name__

    def json_dict(self, use_str_fallback: bool = True, **pydantic_kwargs) -> dict:
        return super().json_dict(use_str_fallback=use_str_fallback, **pydantic_kwargs)
