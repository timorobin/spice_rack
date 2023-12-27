from __future__ import annotations
from typing import Optional, Any
from pydantic import Field, validator
import stackprinter

from spice_rack import _base_classes

__all__ = (
    "GeneralLogAugmentation",
    "TRACEBACK_AUG_STR_ID"
)

TRACEBACK_AUG_STR_ID = "traceback"


class GeneralLogAugmentation(_base_classes.pydantic.AbstractValueModel):
    """general purpose log augmentation object"""
    aug_key: Optional[str] = Field(
        description="the key we use for the log aug formatted data",
        default=None
    )
    aug_desc: Optional[str] = Field(description="the description", default=None)
    data: Any = Field(description="the data for this log aug object, must be json encode-able")

    @validator("data")
    def _reformat_data_for_log(cls, value: Any) -> Any:
        if value == TRACEBACK_AUG_STR_ID:
            tb_data = stackprinter.format(show_vals=None, style="plaintext")
            value = {"traceback_data": tb_data.splitlines()}

        val_attr_maybe = getattr(value, "__as_log_aug__", None)
        if val_attr_maybe is not None:
            if callable(val_attr_maybe):
                value = val_attr_maybe()
            else:
                value = val_attr_maybe

        return value

    def get_aug_key(self) -> str:
        if self.aug_key:
            return self.aug_key
        else:
            return "general-aug-instance"

    def get_aug_desc(self) -> str:
        if self.aug_desc:
            return self.aug_desc
        else:
            return "no description"

    def get_serializable_data(self) -> dict:
        json_data = self.json_dict(use_str_fallback=True)
        return {
            "aug_key": self.aug_key,
            "aug_description": self.aug_desc,
            "aug_data_type": type(self.data).__name__,
            "aug_data": json_data.get("data"),
        }

    @classmethod
    def validate(cls, value: Any) -> GeneralLogAugmentation:
        if isinstance(value, GeneralLogAugmentation):
            return value

        if isinstance(value, dict):
            if "aug_key" in value:
                value = value
            else:
                value = {"data": value}
        else:
            value = {"data": value}

        res = super().validate(value)
        assert isinstance(res, GeneralLogAugmentation), type(res)
        return res
