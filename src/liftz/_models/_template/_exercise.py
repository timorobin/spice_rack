from __future__ import annotations
from pydantic import Field

from spice_rack import base_classes
from liftz._models._record_mixin import RecordMixin
from liftz._models import _common


__all__ = (
    "ExerciseKey",
    "ExerciseTags",
    "Exercise",
    "ExerciseRecord",
    "DayTemplateExerciseItem"
)


class ExerciseKey(base_classes.AbstractSpecialStr):
    """special string for an exercise"""
    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data


class ExerciseTags(base_classes.enums.StrEnum):
    UPPER = "upper"
    LOWER = "lower"


class _ExerciseCommon(base_classes.pydantic.AbstractValueModel):
    """common fields for an exercise for the different exercise representations"""
    key: ExerciseKey = Field(description="the key for this exercise, unique across all lifts")
    description: str = Field(description="the free-form text description")
    tags: list[ExerciseTags] = Field(description="tags for the exercise")


class Exercise(_ExerciseCommon):
    """internal object representing an exercise"""
    ...


class ExerciseRecord(_ExerciseCommon, RecordMixin):
    """record specifying an exercise, like squats or bench"""
    key: ExerciseKey = Field(description="the key for this exercise, unique across all lifts")
    description: str = Field(description="the free-form text description")
    tags: list[ExerciseTags] = Field(description="tags for the exercise")

    @classmethod
    def get_repo_name(cls) -> str:
        return "exercises"


class DayTemplateExerciseItem(base_classes.pydantic.AbstractValueModel):
    """common fields for a task for the different representations"""
    exercise_key: ExerciseKey
    sets: list[_common.SetInfo] = Field(description="the weight and reps to do")
