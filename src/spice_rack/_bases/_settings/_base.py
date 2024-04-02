from __future__ import annotations
import json
import typing as t
from pathlib import Path
import pydantic
import pydantic_settings

from spice_rack._bases._settings import _sources


__all__ = ("SettingsBase", )


# PyCharm IDE works if we do this rather than Self from std lib
Self = t.TypeVar("Self", bound="SettingsBase")


class SettingsBase(pydantic_settings.BaseSettings):
    """
    Base class inheriting from v1 version of Pydantic's BaseSettings.
    This will be adjusted when we fully move to Pydantic v2.

    Notes:
        use double underscores, '__', as the nested delimiter

    References:
        - https://docs.pydantic.dev/1.10/usage/settings/
    """
    _singleton_source: t.ClassVar[t.Optional[_sources.SingletonSource]] = None

    model_config = pydantic_settings.SettingsConfigDict(
        extra="ignore"
    )

    def __init_subclass__(cls, singleton_mode: bool = True, **kwargs):
        if singleton_mode:
            cls._singleton_source = _sources.SingletonSource(
                settings_cls=cls
            )

        super().__init_subclass__(**kwargs)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
        init_settings: pydantic_settings.PydanticBaseSettingsSource,
        env_settings: pydantic_settings.DotEnvSettingsSource,
        dotenv_settings: pydantic_settings.PydanticBaseSettingsSource,
        file_secret_settings: pydantic_settings.PydanticBaseSettingsSource,
    ) -> tuple[pydantic_settings.PydanticBaseSettingsSource, ...]:

        sources: list[pydantic_settings.PydanticBaseSettingsSource] = [
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings
        ]
        if cls._singleton_source:
            sources.insert(1, cls._singleton_source)

        # replace with our extended func
        for src in sources:
            src.decode_complex_value = _decode_complex_value

        return tuple(sources)

    @classmethod
    def _get_dot_env_files(cls) -> list[t.Union[str, Path]]:
        """
        return relative or absolute file paths to .env files in descending precedence, so last
        one specified will be the highest precedence.
        """
        return []

    @classmethod
    def _get_env_nested_delimiter(cls) -> str:
        """
        the delimiter to use when parsing env values. default is double underscore
        """
        return "__"

    @classmethod
    def load(
            cls: t.Type[Self],
            use_cls_env_files: bool = True,
            **kwargs
    ) -> Self:
        env_files: list[str] = []
        for fp in cls._get_dot_env_files():  # type: ignore
            env_files.append(str(fp))

        if use_cls_env_files:
            kwargs["_env_file"] = tuple(env_files)
            kwargs["_env_nested_delimiter"] = cls._get_env_nested_delimiter()

        return cls(**kwargs)


# noinspection PyUnusedLocal
def _decode_complex_value(
        field_name: str,
        field: pydantic.fields.FieldInfo,
        value: t.Any
) -> t.Any:
    """
    overwrite pydantic's 'PydanticBaseSettingsSource' method to allow us to parse complex
    fields that have simple values. pydantic always tries to decode the data as json, even if it isn't.
    """
    try:
        return json.loads(value)

    # if it fails, we just return value directly
    except json.decoder.JSONDecodeError:
        return value

    except Exception as e:
        raise e
