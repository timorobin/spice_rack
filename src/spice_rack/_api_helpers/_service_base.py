from __future__ import annotations
import typing as t
from abc import abstractmethod

from spice_rack import _base_classes, _logging
from spice_rack._api_helpers._common_exceptions import UnknownExceptionWrapper


__all__ = (
    "ApiServiceBase",
)


_http_exc = _base_classes.exception.http
_SuccessRespTV = t.TypeVar("_SuccessRespTV", )
"""the generic param for the return type when no error happens"""


class ApiServiceBase(
    _base_classes.pydantic.AbstractGenericValueModel,
    t.Generic[_SuccessRespTV]
):
    """
    Base class for a unit of functionality that executes.
    You can specify error handling and configure the status codes here.
    This is not an actual api endpoint itself, but your api endpoints
    push as much logic as possible to these classes, and likely end up
    being 1 to 1 coupled.
    """

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def get_logger(self) -> _logging.LoggerT:
        ...

    @classmethod
    def get_module_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def _call(self) -> _SuccessRespTV:
        """
        Put the logic for the service here. Do not raise any exceptions from
        this method. Instead, return an error response.

        Returns:
            _SuccessRespTV: the successful response

        Raises:
            HttpException: an exception we've caught and assigned a status code to
        """
        ...

    def call(self) -> _SuccessRespTV:
        """
        execute the logic, catching any errors, and raising the correct http exception
        with a status code.

        Returns:
            _SuccessRespTV: the successful response

        Raises:
            HttpException: an exception we've caught and assigned a status code to
        """
        try:
            resp = self.call()

        except _http_exc.HttpException as e:
            raise e

        except Exception as e:
            wrapped_exc = UnknownExceptionWrapper(
                caught_exception=e,
                detail=f"uncaught exception in the service named '{self.get_module_name()}'",
                verbose=True,
                extra_info=None
            )
            http_exc = _http_exc.HttpException(
                status_code=500, error_payload=wrapped_exc.get_error_payload_inst()
            )
            raise http_exc from e

        else:
            success_resp: _SuccessRespTV = resp
            return success_resp

    @classmethod
    def _get_standard_response_info(cls) -> list[_http_exc.HttpErrorResponseInfo]:
        """Gets common response info all of them share"""
        return [
            UnknownExceptionWrapper.build_http_response_info_inst(
                status_code=500,
            )
        ]

    @classmethod
    @abstractmethod
    def _get_unique_response_info(
            cls
    ) -> list[_http_exc.HttpErrorResponseInfo]:
        """
        get the list of potential response error models and the related status codes,
        these should be unique to the module. No need to repeat the standard ones.
        The errors specified here should correspond to the ones caught in the '_call' method
        """
        return []

    @classmethod
    @t.final
    def get_response_info(cls) -> list[_http_exc.HttpErrorResponseInfo]:
        return cls._get_standard_response_info() + cls._get_unique_response_info()

    @classmethod
    def get_summary(cls) -> str:
        """a few words describing the service, will be used to describe the endpoint"""
        return "no summary specified"

    @classmethod
    def get_description(cls) -> str:
        """
        a longer description giving more detailed info about the service. Used in the
        description of the endpoint
        """
        return "no description specified"
