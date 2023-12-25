from __future__ import annotations
from pydantic import Field

import spice_rack
from liftz._models._record_mixin import RecordMixin

__all__ = (
    "StrengthExerciseTags",
    "StrengthExerciseDef",
    "StrengthExerciseDefRecord"
)


class StrengthExerciseTags(spice_rack.enum_bases.StrEnum):
    """tags available for a strength exercise"""
    UPPER = "upper"
    LOWER = "lower"


class _StrengthExerciseDefCommon(spice_rack.pydantic_bases.AbstractValueModel):
    """common fields for an exercise for the different exercise representations"""
    key: StrengthExerciseTags = Field(
        description="the key for this exercise, unique across all strength exercises"
    )
    description: str = Field(description="the free-form text description")
    tags: list[StrengthExerciseTags] = Field(description="tags for the exercise")


class StrengthExerciseDef(
    _StrengthExerciseDefCommon
):
    """internal representation of a strength exercise definition"""
    ...


class StrengthExerciseDefRecord(_StrengthExerciseDefCommon, RecordMixin):
    """record defining a strength exercise, like squats or bench"""
    ...

    @classmethod
    def get_repo_name(cls) -> str:
        return "exercises"
