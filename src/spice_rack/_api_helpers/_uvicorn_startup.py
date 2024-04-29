from __future__ import annotations
import typing as t
import typing_extensions
import uvicorn
from uvicorn.supervisors import Multiprocess, ChangeReload
from uvicorn.supervisors.basereload import BaseReload
from pydantic import Field
from spice_rack import _bases


__all__ = (
    "UvicornStartupConfig",
    "start_uvicorn"
)


class _UvicornSslConfig(_bases.ValueModelBase):
    """nested config for configuring ssl to uvicorn the server"""
    keyfile_path: str
    keyfile_password: str
    certfile_path: str


class UvicornStartupConfig(_bases.SettingsBase):
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
        description="num server workers, we only support 1 at the moment.",
        default=1,
        gt=0,
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


def start_uvicorn(
        app: t.Any,
        config: UvicornStartupConfig,
) -> typing_extensions.Never:
    """
    serve an app using the uvicorn server configured with a specified config instance

    Args:
        app: the app we are serving. Should be something like FastApi or litestar instance
        config: the uvicorn config

    Returns:
        Never returns, runs until something kills the process
    """
    ssl_keyfile: t.Optional[str] = None
    ssl_keyfile_password: t.Optional[str] = None
    ssl_certfile: t.Optional[str] = None
    if config.ssl:
        ssl_keyfile = config.ssl.keyfile_path
        ssl_keyfile_password = config.ssl.keyfile_password
        ssl_certfile = config.ssl.certfile_path

    uvicorn_config = uvicorn.Config(
        app=app,
        host=config.host,
        port=config.port,
        reload=config.reload_mode,
        workers=config.num_workers,
        root_path=config.root_path,
        proxy_headers=config.proxy_headers,
        forwarded_allow_ips=config.forwarded_allow_ips,
        ssl_keyfile=ssl_keyfile,
        ssl_keyfile_password=ssl_keyfile_password,
        ssl_certfile=ssl_certfile
    )

    server = uvicorn.Server(config=uvicorn_config)
    supervisor_type: t.Optional[t.Union[t.Type[BaseReload], t.Type[Multiprocess]]] = None
    if uvicorn_config.should_reload:
        supervisor_type = ChangeReload
    if uvicorn_config.workers > 1:
        supervisor_type = Multiprocess
    if supervisor_type:
        sock = uvicorn_config.bind_socket()
        supervisor = supervisor_type(uvicorn_config, target=server.run, sockets=[sock])
        supervisor.run()
    else:
        server.run()

    raise Exception("Should have started a server before reaching this point")
