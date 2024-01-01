from __future__ import annotations
import typing as t
from pathlib import Path

from pydantic.env_settings import BaseSettings


__all__ = ("AbstractSettings", )


# PyCharm IDE works if we do this rather than Self from std lib
Self = t.TypeVar("Self", bound="AbstractSettings")


class AbstractSettings(BaseSettings):
    """
    Base class inheriting from v1 version of Pydantic's BaseSettings.
    This will be adjusted when we fully move to Pydantic v2.

    Notes:
        use double underscores, '__', as the nested delimiter

    References:
        - https://docs.pydantic.dev/1.10/usage/settings/
    """
    class Config:
        extra = "ignore"
        frozen = True
        env_nested_delimiter = "__"

    @classmethod
    def get_dot_env_files(cls) -> list[t.Union[str, Path]]:
        """
        return relative or absolute file paths to .env files in descending precedence, so last
        one specified will be the highest precedence.
        """
        return []

    @classmethod
    def load(
            cls: t.Type[Self],
            use_cls_env_files: bool = True,
            **kwargs
    ) -> Self:
        env_files: list[str] = []
        for fp in cls.get_dot_env_files():
            env_files.append(str(fp))

        if use_cls_env_files:
            kwargs["_env_file"] = tuple(env_files)
        return cls(**kwargs)
