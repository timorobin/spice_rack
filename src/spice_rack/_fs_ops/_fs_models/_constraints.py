from __future__ import annotations
import typing as t
import pydantic
import pydantic_core

from spice_rack._fs_ops import _file_info, _exceptions

if t.TYPE_CHECKING:
    from spice_rack._fs_ops._fs_models._file import FilePath
    from spice_rack._fs_ops._fs_models._types import FileOrDirPathT


__all__ = (
    "ExistsConstraint",
    "FileExtConstraint",
)


# these cannot be pydantic models themselves


class ExistsConstraint:
    """ensures the fs obj path exists"""

    @staticmethod
    def _get_func() -> pydantic_core.core_schema.NoInfoValidatorFunction:
        def _func(fs_obj: FileOrDirPathT) -> FileOrDirPathT:
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


class _FileExtValFunc:
    """used in file extension constraints"""
    def __init__(self, options: t.List[_file_info.FileExt]):
        self.options = options

    def __call__(self, fs_obj: FilePath) -> FilePath:
        try:
            fs_obj.ensure_correct_file_ext(choices=self.options)

        except _exceptions.InvalidFileExtensionException as e:
            raise e.as_pydantic_error()

        except Exception as e:
            raise e

        return fs_obj


_OptionsTypeAdapter = pydantic.TypeAdapter(t.List[_file_info.FileExt])


class _FileExtConstraintBase:
    """base class for a file extension constraint class"""
    _file_ext_options_md_key: t.ClassVar[str] = "valid_file_extensions"
    """key we use in the pydantic schema metadata for the file extension options"""
    def __init__(self, __options: t.List[str]):
        # ensure options is at least one
        self._options: t.List[_file_info.FileExt] = _OptionsTypeAdapter.validate_python(__options)

    def _update_pydantic_schema_metadata(
            self,
            pydantic_schema: pydantic_core.CoreSchema,
    ) -> pydantic_core.CoreSchema:
        _existing_schema_md = pydantic_schema.get("metadata")
        schema_md = _existing_schema_md if _existing_schema_md else {}

        # if not a dict we do nothing bc I'm not sure what's going on
        if isinstance(schema_md, dict):
            schema_md["valid_file_extensions"] = self._options
            pydantic_schema["metadata"] = schema_md
        return pydantic_schema

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = _FileExtValFunc(options=self._options)
        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=val_func,
            schema=schema
        )
        schema = self._update_pydantic_schema_metadata(schema)
        return schema

    def __get_pydantic_json_schema__(
            self,
            core_schema: pydantic_core.CoreSchema,
            handler: pydantic.GetJsonSchemaHandler
    ) -> pydantic.json_schema.JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        current_desc = json_schema.get("description", "")

        description_add_on: str
        if len(self._options) > 1:
            file_ext_options_strs = [f"'{str(option)}'" for option in self._options]
            file_ext_options_str = ", ".join(file_ext_options_strs)
            description_add_on = f"the file must have one of the following extensions: [{file_ext_options_str}]"
        else:
            description_add_on = f"the file must have the '{str(self._options[0])}' file extension"

        updated_desc = f"{current_desc}\n{description_add_on}"
        json_schema["description"] = updated_desc
        return json_schema


class FileExtConstraint(_FileExtConstraintBase):
    """generic file ext constraint, specify the options yourself"""
    def __init__(self, __options: t.Union[str, t.Iterable[str]]):
        if not __options:
            raise ValueError(
                "must specify a list of valid file extensions"
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

        super().__init__(choices)
