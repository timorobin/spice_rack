import pytest
import typing as t
from pathlib import Path
import pydantic

from spice_rack import bases, fs_ops, utils


@pytest.fixture(scope="module")
def dot_env_file_path() -> Path:
    path_obj = Path(__file__).parent.joinpath(".env")
    yield path_obj
    path_obj.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def dot_env_file_builder(dot_env_file_path) -> t.Callable[[t.Dict[str, t.Any]], None]:
    fp_obj = fs_ops.FilePath.model_validate(str(dot_env_file_path))

    def _builder(data: t.Dict) -> None:
        fp_obj.delete(if_non_existent="return")
        data = utils.flatten_dict(data, key_join_strat="__")

        lines = [
            f"{k}={v}" for k, v in data.items()
        ]
        contents = "\n".join(lines)
        fp_obj.write(contents)
    return _builder


def test_simple(dot_env_file_builder, dot_env_file_path):
    class Config(bases.SettingsBase):
        simple: str

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    dot_env_file_builder(
        {"simple": "xxx"}
    )
    c1 = Config.load()
    assert c1.simple == "xxx"

    c2 = Config(simple="abc")
    assert c2.simple == "abc"


def test_file_path(dot_env_file_builder, dot_env_file_path):
    class Config(bases.SettingsBase):
        fp: fs_ops.FilePath

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    dot_env_file_builder(
        {"fp": "$HOME/file.txt"}
    )

    fp_obj = fs_ops.FilePath.model_validate("$HOME/file.txt")
    c1 = Config.load()
    assert c1.fp == fp_obj


def test_optional_file_path(dot_env_file_builder, dot_env_file_path):
    class Config(bases.SettingsBase):
        fp: t.Optional[fs_ops.FilePath] = None

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    dot_env_file_builder({})

    c1 = Config.load()
    assert c1.fp is None


def test_nested_config_subclasses(dot_env_file_builder, dot_env_file_path):
    # see what happens if we nest a fully specified config on another config, will the values conflict?
    class C1(bases.SettingsBase):
        a: str
        b: str

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    class C2(bases.SettingsBase):
        x: str
        y: str
        c1: C1

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    c1_data = {"a": "a", "b": "b"}
    dot_env_file_builder(c1_data)
    assert C1.load().model_dump() == c1_data

    c2_data = {
        "x": "x",
        "y": "y",

        # nested
        "c1": {"a": "a", "b": "b"},
    }
    dot_env_file_builder(c2_data)
    assert C2.load().model_dump() == c2_data

    combo_data = {**c1_data, **c2_data}
    dot_env_file_builder(combo_data)
    assert C1.load().model_dump() == c1_data
    assert C2.load().model_dump() == c2_data

    # without nested specified and add default to c1 field
    class C3(C2):
        c1: C1 = pydantic.Field(default_factory=C1.load)

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    no_nested_data = {
        # top level c1
        "a": "a",
        "b": "b",

        # top level C2
        "x": "x",
        "y": "y"
    }

    dot_env_file_builder(no_nested_data)
    expected_c3_data = {
        "x": "x",
        "y": "y",

        # nested
        "c1": {"a": "a", "b": "b"},
    }
    assert C3.load().model_dump() == expected_c3_data
