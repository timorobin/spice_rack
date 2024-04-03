from __future__ import annotations
import os
from abc import abstractmethod
import typing as t
import pydantic

from spice_rack import _bases
from spice_rack._fs_ops import _path_strs

if t.TYPE_CHECKING:
    from spice_rack._fs_ops._fs_models._base import AbstractFileSystemObj
    from spice_rack._fs_ops._fs_models._file import FilePath
    from spice_rack._fs_ops._fs_models._dir import DirPath


__all__ = (
    "DeferredFilePath", "DeferredDirPath",
)


class _DeferredPath(_bases.DispatchableValueModelBase):
    env_var_key: str

    def _get_env_var_val(self) -> DirPath:
        from spice_rack._fs_ops._fs_models._dir import DirPath

        env_val_maybe = os.environ.get(self.env_var_key)
        if env_val_maybe is None:
            raise ValueError(
                f"'{self.env_var_key}' not found in the environment"
            )
        return DirPath.model_validate(env_val_maybe)

    @abstractmethod
    def evaluate(self) -> AbstractFileSystemObj:
        ...


class DeferredFilePath(_DeferredPath):
    """
    a file path, where part of the path is contained in an environment variable, that is
    looked up when we call 'evaluate' method to convert this instance to a FilePath instance.
    """
    rel_path: _path_strs.RelFilePathStr

    @pydantic.model_validator(mode="before")
    def _handle_str(cls, data: t.Any) -> t.Any:
        if isinstance(data, str):
            if "/" not in data:
                raise ValueError(
                    f"'{data}' cannot be parsed as "
                    f"'{cls.get_class_id()}' bc it has not relative file path beyond"
                    f"the deferred environment key"
                )

            split = data.split("/")
            env_var_key = split[0].replace("$", "")
            rel_path = "/".join(split[1:])

            data = {"env_var_key": env_var_key, "rel_path": rel_path}
        return data

    def evaluate(self) -> FilePath:
        env_val = self._get_env_var_val()
        return env_val.joinpath(self.rel_path)


class DeferredDirPath(_DeferredPath):
    """
    a dir path, where part or all of the path is contained in an environment variable, that is
    looked up when we call 'evaluate' method to convert this instance to a DirPath instance.
    """
    rel_path: t.Optional[_path_strs.RelDirPathStr]

    @pydantic.model_validator(mode="before")
    def _handle_str(cls, data: t.Any) -> t.Any:
        if isinstance(data, str):
            split = data.split("/")
            env_var_key = split[0].replace("$", "")
            rel_path = "/".join(split[1:])
            if not rel_path or rel_path == "/":
                rel_path = None
            data = {"env_var_key": env_var_key, "rel_path": rel_path}
        return data

    def evaluate(self) -> DirPath:
        env_val = self._get_env_var_val()
        if self.rel_path:
            return env_val.joinpath(self.rel_path)
        else:
            return env_val
