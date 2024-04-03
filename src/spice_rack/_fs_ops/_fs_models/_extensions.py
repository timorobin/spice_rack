# """convenience objects that wrap core objects, extending their functionality."""
# from __future__ import annotations
# import typing as t
# import pydantic
#
# from spice_rack import _bases
# from spice_rack._fs_ops._fs_models import _core, _constraints
#
#
# __all__ = (
#     "YamlFilePath",
#     "JsonFilePath"
# )
#
#
# class YamlFilePath(
#     _bases.RootModel[
#         t.Annotated[_core.FilePath, _constraints.YamlFileConstraint()]
#     ]
# ):
#     """
#     an extension for yaml files with yaml-specific operations.
#
#     Notes:
#         Use 'root' attribute to access to the FilePath object and its interface. This wrapper only
#         implements yaml-specific methods.
#     """
#
#     def yaml_write(self, data: t.Union[pydantic.JsonValue, pydantic.BaseModel]) -> None:
#         ...
#
#     def yaml_read(self) -> pydantic.JsonValue:
#         ...
#
#
# class JsonFilePath(
#     _bases.RootModel[
#         t.Annotated[_core.FilePath, _constraints.JsonFileConstraint()]
#     ]
# ):
#     """
#     an extension for json files with some specific operations.
#
#     Notes:
#         Use 'root' attribute to access to the FilePath object and its interface. This wrapper only
#         implements json-specific methods.
#     """
#     def json_write(self, data: t.Union[pydantic.JsonValue, pydantic.BaseModel]) -> None:
#         ...
#
#     def json_read(self) -> pydantic.JsonValue:
#         ...
