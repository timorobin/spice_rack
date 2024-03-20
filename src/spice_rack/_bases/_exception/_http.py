from __future__ import annotations
import typing as t
from inspect import getdoc
from pydantic import Field

from spice_rack._bases import _value_model
from spice_rack._bases._exception._exception_base import CustomExceptionBase
from spice_rack._bases._exception._error_info import ErrorInfoBase, ErrorPayload
from spice_rack._bases._exception._external_wrapper import WrappedExternalException


__all__ = (
    "HttpException",
    "HttpErrorResponseInfo",
    "UnknownExceptionWrapper",
    "RequestValidationException",
)


class _UnknownExceptionErrorInfo(ErrorInfoBase):
    """
    An unexpected exception was encountered, i.e. not one of our subclasses.
    Wrapping it with this class allows us to work it into our exception handling and other
    tooling.
    """
    caught_exception: WrappedExternalException = Field(
        description="the exception we encountered"
    )


class UnknownExceptionWrapper(CustomExceptionBase[_UnknownExceptionErrorInfo]):
    """
    An unexpected exception was encountered, i.e. not one of our subclasses.
    Wrapping it with this class allows us to work it into our
    exception handling and other tooling.

    Notes:
        - a custom "detail" can be specified, or left blank, in which case we use the str
          representation of the caught exception
    """
    def __init__(
            self,
            caught_exception: Exception,
            detail: t.Optional[str] = None,
            verbose: bool = True,
            extra_info: t.Optional[dict] = None
    ):
        error_info = {
            "caught_exception": caught_exception,
        }
        if detail is None:
            detail = str(caught_exception)
        super().__init__(
            detail=detail,
            error_info=error_info,
            extra_info=extra_info,
            verbose=verbose
        )


class HttpErrorResponseInfo(_value_model.ValueModelBase):
    """
    Holds the status code and the exception class for a given endpoint.
    This is used to inform endpoints about the potential error responses, and their
    schemas.
    """
    status_code: int = Field(
        description="the status code for the response in question"
    )
    custom_desc: t.Optional[str] = Field(
        description="the custom specified description for this status code for the given endpoint"
    )
    exception_type: t.Type[CustomExceptionBase] = Field(
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


ErrorInfoTV = t.TypeVar("ErrorInfoTV", bound=ErrorInfoBase)


# todo: will delete one of these
class HttpErrorResponse(_value_model.ValueModelBase, t.Generic[ErrorInfoTV]):
    """
    generic container holding an exception payload and a specified status code.

    This is not an exception, so must be treated as a valid return type, and thus should be
    caught and the proper response raised.
    """
    # class Config:
    #     arbitrary_types_allowed = True

    status_code: int = Field(
        description="the status code for the response in question"
    )
    error_payload: ErrorPayload[ErrorInfoTV] = Field(
        description="the payload containing data about this error"
    )


class HttpException(Exception, t.Generic[ErrorInfoTV]):
    """
    generic container holding an exception instance and a specified status code.

    This is an exception
    """
    def __init__(
            self,
            status_code: int,
            error_payload: ErrorPayload[ErrorInfoTV]
    ):
        self.status_code = status_code
        self.error_payload = error_payload
        super().__init__(error_payload.detail)


# todo: figure out the correct inner type
_PydanticValidationErrorT: t.TypeAlias = t.Any
"""this is the data type of pydantic validation errors"""


class _RequestValidationErrorInfo(ErrorInfoBase):
    """
    The request fails to validate, so we don't even get the execute the endpoint.
    This is a wrapper around FastAPI's RequestValidationError.
    """
    issues: list[_PydanticValidationErrorT] = Field(
        description="the validation errors encountered"
    )


class RequestValidationException(
    CustomExceptionBase[_RequestValidationErrorInfo]
):
    """
    The request fails to validate, so we don't even get the execute the endpoint.
    This is a wrapper around FastAPI's RequestValidationError.
    """
    def __init__(
            self,
            detail: str,
            errors: list[_PydanticValidationErrorT],
            verbose: bool = True,
            extra_info: t.Optional[dict] = None
    ):
        error_info = {
            "issues": errors,
        }

        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info,
        )
