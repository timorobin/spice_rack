from __future__ import annotations
import typing as t
import pydantic
import pydantic_core

from spice_rack._fs_ops import _fs_models, _file_info, _exceptions


__all__ = (
    "ExistsConstraint",
    "FileExtConstraint",
    "JsonFileConstraint",
    "YamlFileConstraint"
)


# these cannot be pydantic models themselves


class ExistsConstraint:
    """ensures the fs obj path exists"""

    @staticmethod
    def _get_func() -> pydantic_core.core_schema.NoInfoValidatorFunction:
        def _func(fs_obj: _fs_models.FileOrDirPathT) -> _fs_models.FileOrDirPathT:
            try:
                fs_obj.ensure_exists()

            except _exceptions.NonExistentPathException as e:
                raise e.as_pydantic_error()

            except Exception as e:
                raise e

            return fs_obj
        return _func

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self._get_func()

        # todo: add info to the schema
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=val_func,
            schema=schema
        )
        return schema


class FileExtConstraint:
    choices: t.List[_file_info.FileExt]

    def __init__(self, __options: t.Union[str, t.Iterable[str]]):
        if not __options:
            raise ValueError(
                f"must specify a list of valid file extensions"
            )

        choices: t.List[_file_info.FileExt]
        if isinstance(__options, str):
            choices = [_file_info.FileExt(__options)]
        elif isinstance(__options, t.Iterable):
            choices = [_file_info.FileExt(c) for c in __options]
        else:
            raise ValueError(
                f"must specify valid file extensions as an iterable of strings or a str. received '{__options}'"
            )

        self.choices = choices

    def get_func(self) -> pydantic_core.core_schema.NoInfoValidatorFunction:

        def _func(fs_obj: _fs_models.FilePath) -> _fs_models.FileOrDirPathT:
            try:
                fs_obj.ensure_correct_file_ext(choices=self.choices)

            except _exceptions.InvalidFileExtensionException as e:
                raise e.as_pydantic_error()

            except Exception as e:
                raise e

            return fs_obj
        return _func

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self.get_func()

        # todo: add info to the schema
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=val_func,
            schema=schema
        )
        return schema


class JsonFileConstraint:
    def __init__(self):
        self._constraint = FileExtConstraint(["json"])

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self._constraint.get_func()

        # todo: add info to the schema
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=val_func,
            schema=schema
        )
        return schema


class YamlFileConstraint:
    def __init__(self):
        self._constraint = FileExtConstraint(["yaml", "yml"])

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self._constraint.get_func()

        # todo: add info to the schema
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=val_func,
            schema=schema
        )
        return schema
