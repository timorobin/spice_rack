import pytest
from parametrization import Parametrization as PytestParamExt
from typing import Optional, Any, Union

from spice_rack import bases


class _SimpleErrorInfo(bases.exceptions.ErrorInfoBase):
    num: int
    arr: list[str]


class _SimpleException(bases.exceptions.CustomExceptionBase[_SimpleErrorInfo]):
    def __init__(
            self,
            error_info: Union[_SimpleErrorInfo, dict],
            verbose: bool,
            extra_info: Optional
    ):
        detail = "some simple error"
        super().__init__(
            detail=detail,
            error_info=error_info,
            verbose=verbose,
            extra_info=extra_info
        )


def test_info_cls_getter():
    error_info_cls = _SimpleException.get_error_info_cls()
    assert error_info_cls == _SimpleErrorInfo


def test_payload_cls_getter():
    assert _SimpleException.get_error_payload_cls()


class _ExceptionTestScenario(bases.value_model.ValueModelBase):
    name: str
    detail: str = "some simple error"
    num: int = 2
    arr: list[str] = ["x", "y"]
    extra_info: Optional[dict] = None
    http_status_code: Optional[int] = None

    def __repr__(self) -> str:
        return self.name


@PytestParamExt.parameters("scenario")
@PytestParamExt.name_factory(
    lambda scenario: repr(scenario)
)
@PytestParamExt.case(
    scenario=_ExceptionTestScenario(name="no_extra_no_status")
)
@PytestParamExt.case(
    scenario=_ExceptionTestScenario(
        name="with_extra_info",
        extra_info={"extra_field": "abc"}
    )
)
def test_formatting(scenario: _ExceptionTestScenario) -> None:
    exc_inst_verbose = _SimpleException(
        error_info=dict(
            num=scenario.num,
            arr=scenario.arr,
        ),
        extra_info=scenario.extra_info,
        verbose=True
    )
    assert exc_inst_verbose.detail == scenario.detail
    assert str(exc_inst_verbose) != scenario.detail
    if scenario.extra_info:
        expected_extra_info = scenario.extra_info
    else:
        expected_extra_info = {}

    assert exc_inst_verbose.error_info.extra == expected_extra_info

    exc_inst_terse = _SimpleException(
        error_info=dict(
            num=scenario.num,
            arr=scenario.arr,
        ),
        extra_info=scenario.extra_info,
        verbose=False
    )
    assert exc_inst_terse.detail == scenario.detail
    assert str(exc_inst_terse) == scenario.detail
    assert exc_inst_terse.error_info.extra == expected_extra_info

    exc_inst_info_obj = _SimpleException(
        error_info=_SimpleErrorInfo(
            num=scenario.num,
            arr=scenario.arr,
        ),
        extra_info=scenario.extra_info,
        verbose=True
    )
    assert exc_inst_info_obj.error_info == exc_inst_terse.error_info


class _BadInitScenario(bases.value_model.ValueModelBase):
    name: str
    detail: str = "some simple error"
    num: Any = 2
    arr: Any = ["x", "y"]
    extra_info: Optional[dict] = None


@PytestParamExt.parameters("scenario")
@PytestParamExt.name_factory(
    lambda scenario: repr(scenario)
)
@PytestParamExt.case(
    scenario=_BadInitScenario(
        name="wrong_error_info_attr_type",
        num="abc"
    ),
)
def test_exception_bad_init(scenario: _BadInitScenario):
    with pytest.raises(bases.exceptions.CustomExceptionInitializationError):
        _SimpleException(
            error_info=dict(
                num=scenario.num,
                arr=scenario.arr,
            ),
            extra_info=scenario.extra_info,
            verbose=True
        )
    with pytest.raises(bases.exceptions.CustomExceptionInitializationError):
        _SimpleException(
            error_info=dict(
                num=scenario.num,
                arr=scenario.arr,
            ),
            extra_info=scenario.extra_info,
            verbose=False
        )


def test_no_error_info_class_specified():
    with pytest.raises(ValueError):
        class _BadException(bases.exceptions.CustomExceptionBase):
            ...
        from devtools import debug
        debug(_BadException.get_error_info_cls())
