import pytest
import typing as t
from pathlib import Path

from spice_rack import bases, fs_ops


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
