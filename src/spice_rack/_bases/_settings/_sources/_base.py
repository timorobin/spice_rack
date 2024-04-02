from __future__ import annotations
import typing as t
from abc import abstractmethod

import pydantic_settings

__all__ = (
    "CustomSettingSourceBase",
)


class CustomSettingSourceBase(pydantic_settings.PydanticBaseSettingsSource):
    """base class for a custom settings_base source. matches specified format pydantic wants"""
    @abstractmethod
    def __call__(self) -> dict[str, t.Any]:
        ...
