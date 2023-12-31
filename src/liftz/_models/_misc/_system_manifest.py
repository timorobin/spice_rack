from __future__ import annotations
import typing as t
import yaml

from pydantic import Field

import spice_rack

if t.TYPE_CHECKING:
    from liftz._models import _program_template, _strength_exercise

__all__ = (
    "SystemManifest",
)

_FilePathT = str
# todo: replace with proper file path


class _TempUserCreate(spice_rack.pydantic_bases.AbstractValueModel):
    """temp object we will stop using once we set up auth properly"""
    name: str
    email: str
    password: str
    is_superuser: bool = False


class SystemManifest(spice_rack.pydantic_bases.AbstractValueModel):
    """holds initial assets to load into the db"""
    users: list[_TempUserCreate] = Field(
        description="default users", default_factory=list
    )
    strength_exercises: list[_strength_exercise.StrengthExerciseDef] = Field(
        description="default users", default_factory=list
    )
    program_templates: list[_program_template.ProgramTemplate] = Field(
        description="default users", default_factory=list
    )

    @classmethod
    def validate_system_manifest_fp(cls, fp: _FilePathT) -> None:
        if not fp.endswith(".yaml") or fp.endswith(".yml"):
            raise ValueError(
                f"'{fp}' is not a yaml file."
            )

    @classmethod
    def load_from_file_path(cls, fp: _FilePathT) -> SystemManifest:
        cls.validate_system_manifest_fp(fp)

        with open(fp, mode="r") as f:
            data = yaml.unsafe_load(f)
        return SystemManifest.parse_obj(data)

    def save_to_file_path(self, fp: _FilePathT) -> None:
        self.validate_system_manifest_fp(fp)

        data = self.json_dict()
        with open(fp, mode="w+") as f:
            yaml.dump(data, f)

    @classmethod
    def _import_forward_refs(cls) -> dict:
        from liftz._models import _program_template, _strength_exercise
        return {
            "_program_template": _program_template,
            "_strength_exercise": _strength_exercise,
        }
