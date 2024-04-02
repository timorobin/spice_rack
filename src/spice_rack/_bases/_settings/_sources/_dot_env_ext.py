from __future__ import annotations
import typing as t

from pydantic import PrivateAttr
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings
from spice_rack._bases._settings._sources import _base

if t.TYPE_CHECKING:
    from spice_rack._bases._settings._base import SettingsBase


__all__ = (
    "SingletonSource",
)


SettingsInstTV = t.TypeVar("SettingsInstTV", bound=BaseSettings)


class SingletonSource(_base.CustomSettingSourceBase, t.Generic[SettingsInstTV]):
    """stores prior reads and uses them if available"""
    settings_cls: t.Type[BaseSettings]
    _registry: _Registry[SettingsInstTV] = PrivateAttr()

    def __init__(self, settings_cls: t.Type[SettingsInstTV]):
        super().__init__(settings_cls=settings_cls)

        settings_cls: t.Type[BaseSettings] = self.settings_cls  # type: ignore
        self._registry = _Registry[settings_cls]()  # type: ignore

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[t.Any, str, bool]:

        # copied this from the implementation for another settings_base source in pydantic_settings
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, '', False

    def __call__(self) -> dict[str, t.Any]:
        cached_inst_maybe = self._registry.get_maybe(self.settings_cls)  # type: ignore
        if cached_inst_maybe:
            return cached_inst_maybe.model_dump()
        else:
            return {}

    def add_to_registry(self, inst: SettingsInstTV) -> None:
        self._registry.cache(inst)


class _Registry(t.Generic[SettingsInstTV]):
    def __init__(self):
        self._registry: dict[t.Type[SettingsInstTV], SettingsInstTV] = {}    # type: ignore

    def get_maybe(
            self,
            settings_cls: t.Type[SettingsInstTV]
    ) -> t.Optional[SettingsBase]:
        return self._registry.get(settings_cls)  # type: ignore

    def cache(
            self,
            settings_inst: SettingsInstTV
    ) -> None:
        self._registry[type(settings_inst)] = settings_inst
