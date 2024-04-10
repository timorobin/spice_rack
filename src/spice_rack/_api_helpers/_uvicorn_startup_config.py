from __future__ import annotations
import typing as t
from pydantic import Field
from spice_rack import bases


__all__ = (
    "UvicornStartupConfig",
)


class _UvicornSslConfig(bases.ValueModelBase):
    """nested config for configuring ssl to uvicorn the server"""
    keyfile_path: str
    keyfile_password: str
    certfile_path: str


class UvicornStartupConfig(bases.SettingsBase):
    """
    config subsection for starting up an uvicorn process, useful for APIs such as litestar or fastapi.

    default env_prefix is 'uvicorn_startup__'
    """
    host: str = Field(default="localhost", description="host name of the app process")
    port: int = Field(default=8000, description="port the app is listening on")
    root_path: str = Field(description="used in the fastapi app instance", default="")
    reload_mode: bool = Field(
        default=False, description="whether or not to auto-reload if any changes "
                                   "to the underlying folders occur."
                                   " This should be false in prod"
    )
    num_workers: int = Field(
        description="num server workers, just do 1 for now as anything else is untested",
        default=1
    )
    proxy_headers: bool = Field(
        description="passed to uvicorn config",
        default=False
    )
    forwarded_allow_ips: t.Optional[t.Union[list[str], str]] = Field(
        description="passed to uvicorn config",
        default=None
    )
    ssl: t.Optional[_UvicornSslConfig] = Field(
        description="ssl config stuff for the user, don't use this in production",
        default=None
    )

    @classmethod
    def _get_env_prefix(cls) -> t.Optional[str]:
        return f"uvicorn_startup{cls._get_env_nested_delimiter()}"
