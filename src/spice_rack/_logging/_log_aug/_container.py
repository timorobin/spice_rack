from __future__ import annotations
import typing as t
import pydantic
import stackprinter
import devtools

from spice_rack import _bases

__all__ = (
    "ExtraLogData",
    "TRACEBACK_AUG_STR_ID",
    "ExtraLogDataContainer",
)


TRACEBACK_AUG_STR_ID = "traceback"


class ExtraLogData(_bases.value_model.ValueModelBase):
    """general purpose log augmentation object"""
    key: str = pydantic.Field(
        description="the key we use for the log aug formatted data",
    )
    desc: str = pydantic.Field(description="the description", default="no description")
    data: t.Any = pydantic.Field(
        description="the data for this log aug object, must be json encode-able"
    )

    @pydantic.computed_field
    def data_type(self) -> str:
        """the class name of the data type"""
        return type(self.data).__name__

    def get_serializable_data(self) -> dict:
        return self.json_dict(use_str_fallback=True)

    @classmethod
    def parse_from_raw_data(cls, data: t.Any) -> ExtraLogData:
        # parse raw data of different types

        # if we find formatting logic, use that
        from spice_rack._logging._log_aug._loggable_mixin import LoggableObjMixin
        if isinstance(data, LoggableObjMixin):
            data = data.__format_for_logger__()

        # check types
        if isinstance(data, ExtraLogData):
            data = data

        elif isinstance(data, str):
            if data == TRACEBACK_AUG_STR_ID:
                tb_data = stackprinter.format(show_vals=None, style="plaintext")
                data = {"key": "some_traceback", "data": tb_data.splitlines()}
            else:
                data = {"key": "some_str_data", "data": data}

        # wrap exceptions in our internal wrapper to get better formatting
        elif isinstance(data, Exception):
            from spice_rack import _bases
            wrapped_exc = _bases.exceptions.WrappedExternalException.model_validate(data)
            data = {
                "key": "logged_exception",
                "data": wrapped_exc.json_dict(use_str_fallback=True)
            }

        # we just specify its type and treat it as data
        else:
            data = {"key": "some_data", "data": data}

        return ExtraLogData.model_validate(data)


class ExtraLogDataContainer(pydantic.RootModel[t.List[ExtraLogData]]):
    def get_logger_repr(self) -> str:
        serialized_data = [item.get_serializable_data() for item in self.root]
        return devtools.pformat(serialized_data)
