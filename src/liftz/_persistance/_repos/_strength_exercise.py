from __future__ import annotations
from typing import ClassVar
from sqlmodel import Field

import spice_rack
from liftz import _models
from liftz._persistance._repos import _record_base


__all__ = (
    "StrengthExerciseTagsStr",
    "StrengthExerciseRecord"
)


class StrengthExerciseTagsStr(spice_rack.AbstractSpecialStr):
    """string of combined enum values, joined by a comma"""
    _sep: ClassVar[str] = ","

    @classmethod
    def _format_str(cls, root_data: str) -> str:
        for part in root_data.split(cls._sep):
            _models.strength_exercise.StrengthExerciseTags(part)
        return root_data

    @classmethod
    def from_tag_list(cls, tags: list[_models.strength_exercise.StrengthExerciseTags]) -> str:
        member_strs = [m.value for m in tags]
        return cls(cls._sep.join(member_strs))

    def to_tag_list(self) -> list[_models.strength_exercise.StrengthExerciseTags]:
        tags = []
        for part in self.split(self._sep):
            tags.append(
                _models.strength_exercise.StrengthExerciseTags(part)
            )
        return tags


class StrengthExerciseRecord(_record_base.TableBase):
    """record of strength exercises"""
    key: _models.strength_exercise.StrengthExerciseKey = Field(
        description="the key", primary_key=True
    )
    tags: StrengthExerciseTagsStr = Field(description="a string representation of a list of tags")

    @classmethod
    def get_table_name(cls) -> str:
        return "strength_exercises"
