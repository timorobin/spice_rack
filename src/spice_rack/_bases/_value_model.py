from __future__ import annotations
import pydantic

from spice_rack._bases import _base_base

__all__ = (
    "VALUE_MODEL_CONFIG",
    "ValueModelBase"
)

_value_config = pydantic.ConfigDict(
    frozen=True,
    extra="forbid",
)
VALUE_MODEL_CONFIG = _base_base.BASE_MODEL_CONFIG.update(_value_config)


class ValueModelBase(pydantic.BaseModel, _base_base.CommonModelMethods):
    """a frozen model"""
    model_config = VALUE_MODEL_CONFIG
