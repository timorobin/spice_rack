from __future__ import annotations
import types
import typing as t
from typing_extensions import LiteralString
from devtools import pformat
from pydantic_core import PydanticCustomError

from spice_rack._bases._exception import _error_info, _exception_exception

if t.TYPE_CHECKING:
    from spice_rack._bases._exception import _http


__all__ = (
    "CustomExceptionBase",
)


Self = t.TypeVar("Self", bound="CustomExceptionBase")
"""pycharm type checker supports this, but it is same as new 'Self' type ann"""

ErrorInfoTV = t.TypeVar("ErrorInfoTV", bound=_error_info.ErrorInfoBase)


class CustomExceptionBase(Exception, t.Generic[ErrorInfoTV]):
    """
    Base for a custom-built exception class.

    Note:
        the typing for the
    """
    _error_info_cls: t.ClassVar[t.Type[_error_info.ErrorInfoBase]] = None  # type: ignore

    _detail: str
    _verbose: bool
    _error_info_inst: ErrorInfoTV

    def __class_getitem__(cls, item: t.Union[t.TypeVar, t.Type[_error_info.ErrorInfoBase]]):

        error_info_cls: t.Type[_error_info.ErrorInfoBase]

        # if manually set, just keep that
        if cls._error_info_cls is not None:
            error_info_cls = cls._error_info_cls
        else:
            try:
                if isinstance(item, t.TypeVar):
                    # if a type var, make sure we have a bound, and use that
                    if item.__bound__:
                        error_info_cls = item.__bound__
                    else:
                        raise ValueError(
                            f"'{item}' is a type var, and must have a bound set"
                        )

                elif issubclass(item, _error_info.ErrorInfoBase):
                    error_info_cls = item

                else:
                    raise ValueError(f"unable to set error info class from the item, {item}")

            except Exception as e:
                raise ValueError(
                    f"error encountered trying to get error info class from type var, error: {e}"
                ) from e

        intermediate_cls_name = f"{cls.__name__}__{item.__name__}"
        new_cls: t.Type[CustomExceptionBase] = t.cast(
            t.Type[CustomExceptionBase],
            types.new_class(
                intermediate_cls_name, bases=(cls, ),
                kwds={"error_info_cls": error_info_cls}
            )
        )
        return new_cls

    def __init_subclass__(
            cls,
            error_info_cls: t.Optional[t.Type[_error_info.ErrorInfoBase]] = None,
            **kwargs
    ):
        if error_info_cls is None and cls._error_info_cls is None:
            raise ValueError(f"{cls.__name__} must specify error info class'")
        elif error_info_cls is not None:
            cls._error_info_cls = error_info_cls
        super().__init_subclass__(**kwargs)

    def __init__(
            self,
            detail: str,
            error_info: t.Union[ErrorInfoTV, dict],
            verbose: bool = True,
            extra_info: t.Optional[dict] = None
    ):
        self.get_error_info_cls().model_rebuild()

        self._detail = detail
        self._verbose = verbose

        try:
            self._error_info_inst = self.get_error_info_cls().model_validate(error_info)

        except Exception as e:
            raise _exception_exception.CustomExceptionInitializationError(
                detail="error info provided failed validation",
                caught_exception=e
            ) from e

        if extra_info:
            self._error_info_inst.extra.update(extra_info)
        formatted_str: str
        if self.verbose:
            formatted_str = self._get_formatted_str_verbose()
        else:
            formatted_str = self._get_formatted_str_terse()

        super().__init__(formatted_str)

    @property
    def detail(self) -> str:
        return self._detail

    @property
    def verbose(self) -> bool:
        return self._verbose

    @property
    def error_info(self: Self) -> ErrorInfoTV:
        return self._error_info_inst

    @classmethod
    def get_error_info_cls(cls: t.Type[Self]) -> t.Type[ErrorInfoTV]:
        return cls._error_info_cls  # type: ignore

    @classmethod
    @t.final
    def get_error_payload_cls(cls: t.Type[Self]) -> t.Type[_error_info.ErrorPayload[ErrorInfoTV]]:
        """
        Returns: an ErrorPayload class parameterized with the correct
        concrete subclass of ErrorInfoBase
        """
        payload_cls = _error_info.ErrorPayload[cls.get_error_info_cls()]  # type: ignore
        return payload_cls

    @t.final
    def get_error_payload_inst(self: Self) -> _error_info.ErrorPayload[ErrorInfoTV]:
        return _error_info.ErrorPayload[self.get_error_info_cls()](
            detail=self.detail,
            error_type=type(self).__name__,
            info=self.error_info,
        )

    def _get_formatted_str_verbose(self) -> LiteralString:
        return pformat(self.get_error_payload_inst().json_dict(use_str_fallback=True))

    def _get_formatted_str_terse(self) -> LiteralString:
        return t.cast(LiteralString, self.detail)

    def as_http_error_resp(
            self,
            status_code: int
    ) -> _http.HttpErrorResponse[ErrorInfoTV]:
        from spice_rack._bases._exception import _http
        return _http.HttpErrorResponse[self._error_info_cls](
            status_code=status_code,
            error_payload=self.get_error_payload_inst()
        )

    def as_http_error_exc(
            self,
            status_code: int
    ) -> _http.HttpException[ErrorInfoTV]:
        from spice_rack._bases._exception import _http
        return _http.HttpException[self._error_info_cls](
            status_code=status_code,
            error_payload=self.get_error_payload_inst()
        )

    @classmethod
    @t.final
    def get_http_response_info_inst(
            cls,
            status_code: int,
            custom_desc: t.Optional[str] = None
    ) -> _http.HttpErrorResponseInfo:
        """build a HttpErrorResponseInfo inst for this exception class"""
        from spice_rack._bases._exception import _http
        return _http.HttpErrorResponseInfo(
            status_code=status_code,
            exception_type=cls,
            custom_desc=custom_desc
        )

    def as_pydantic_error(self, manual_verbose: t.Optional[bool] = None) -> PydanticCustomError:
        verbose: bool
        if manual_verbose is not None:
            verbose = manual_verbose
        else:
            verbose = self.verbose

        if verbose:
            msg = self._get_formatted_str_verbose()
        else:
            msg = self._get_formatted_str_terse()

        error_type = t.cast(LiteralString, self.__class__.__name__)

        return PydanticCustomError(error_type, msg)
