import pytest
import typing as t
from pathlib import Path
import pydantic
import devtools

from spice_rack import bases, fs_ops, utils


@pytest.fixture(scope="module")
def dot_env_file_path() -> Path:
    path_obj = Path(__file__).parent.joinpath(".env")
    yield path_obj
    path_obj.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def dot_env_file_builder(
        dot_env_file_path,
) -> t.Callable[[t.Dict[str, t.Any]], None]:
    fp_obj = fs_ops.FilePath.model_validate(str(dot_env_file_path))

    def _builder(
            data: t.Dict,
    ) -> None:
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


def test_env_prefix(dot_env_file_builder, dot_env_file_path):
    # see what happens if we nest a fully specified config on another config, will the values conflict?
    class C1(bases.SettingsBase):
        a: str
        b: str

        @classmethod
        def _get_env_prefix(cls) -> t.Optional[str]:
            return "c1"

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    c1_data = {"a": "a", "b": "b"}
    # write with the prefix
    dot_env_file_builder({f"c1{k}": v for k, v in c1_data.items()})
    devtools.pprint(dot_env_file_path.read_text().splitlines())
    assert C1.load().model_dump() == c1_data


def test_nested_config_subclass(dot_env_file_builder, dot_env_file_path):
    # see what happens if we nest a fully specified config on another config, in a few common recipes
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


def test_nested_config_subclass_w_prefix(dot_env_file_builder, dot_env_file_path):
    # see what happens if we nest a fully specified config on another config, will the values conflict?
    class C1(bases.SettingsBase):
        a: str
        b: str

        @classmethod
        def _get_env_prefix(cls) -> t.Optional[str]:
            return f"c1{cls._get_env_nested_delimiter()}"

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    c1_data = {"a": "a", "b": "b"}
    c1_prefixed_data = {f"c1__{k}": v for k, v in c1_data.items()}
    # write with the prefix
    dot_env_file_builder(c1_prefixed_data)
    devtools.pprint(dot_env_file_path.read_text().splitlines())
    assert C1.load().model_dump() == c1_data

    class C2(bases.SettingsBase):
        x: str
        y: str
        c1: C1 = pydantic.Field(
            default_factory=C1.load
        )

        @classmethod
        def _get_dot_env_files(cls) -> t.List[Path]:
            return [dot_env_file_path]

    # ignores the prefix on C1
    c2_data = {
        "x": "x",
        "y": "y",

        # nested
        "c1": {"a": "l", "b": "m"},
    }

    dot_env_file_builder(c2_data)
    assert C2.load().model_dump() == c2_data

    # the nested takes precedence
    combined = {**c1_data, **c2_data}
    dot_env_file_builder(combined)
    assert C2.load().model_dump() == c2_data

    # the default still requires the prefix
    combined.pop("c1")
    dot_env_file_builder(combined)
    expected_data = dict(**c2_data)
    expected_data["c1"] = c1_data
    assert C2.load().model_dump() == expected_data
