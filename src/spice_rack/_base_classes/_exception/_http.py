from __future__ import annotations
from typing import Generic, TypeVar, Type, Optional
from inspect import getdoc
from pydantic import Field

from spice_rack._base_classes import _pydantic
from spice_rack._base_classes._exception import _error_info, _exception_base, _types


__all__ = (
    "HttpErrorResponseInfo",
    "HttpErrorResponse",
    "HttpException"
)


class HttpErrorResponseInfo(_pydantic.AbstractValueModel):
    """
    Holds the status code and the exception class for a given endpoint.
    This is used to inform endpoints about the potential error responses, and their
    schemas.
    """
    status_code: _types.HttpStatusCodeT = Field(
        description="the status code for the response in question"
    )
    custom_desc: Optional[str] = Field(
        description="the custom specified description for this status code for the given endpoint"
    )
    exception_type: Type[_exception_base.CustomExceptionBase] = Field(
        description="the type of exception this error response will contain. This will "
                    "dictate schema of the resulting payload associated with the "
                    "response in question."
    )

    def get_desc(self) -> str:
        """
        use custom description if we have it, and use the docstring of the exception class if not
        """
        if self.custom_desc:
            return self.custom_desc
        else:
            docstring_maybe = getdoc(self.exception_type)
            if docstring_maybe:
                return docstring_maybe
            else:
                return f"a '{self.exception_type.__name__}' exception"


ErrorInfoTV = TypeVar("ErrorInfoTV", bound=_error_info.ErrorInfoBase)


class HttpErrorResponse(_pydantic.AbstractGenericValueModel, Generic[ErrorInfoTV]):
    """
    generic container holding an exception payload and a specified status code.

    This is not an exception, so must be treated as a valid return type, and thus should be
    caught and the proper response raised.
    """
    status_code: _types.HttpStatusCodeT = Field(
        description="the status code for the response in question"
    )
    error_payload: _error_info.ErrorPayload[ErrorInfoTV] = Field(
        description="the payload containing data about this error"
    )


class HttpException(Exception, Generic[ErrorInfoTV]):
    """
    generic container holding an exception instance and a specified status code.

    This is an exception
    """
    def __init__(
            self,
            status_code: _types.HttpStatusCodeOrIntT,
            error_payload: _error_info.ErrorPayload[ErrorInfoTV]
    ):
        self.status_code = status_code
        self.error_payload = error_payload
        super().__init__(error_payload.detail)
