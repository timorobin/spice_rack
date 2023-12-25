from __future__ import annotations
from pydantic import Field

import spice_rack

from liftz._models import _misc, _strength_exercise


__all__ = (
    "ProgramTemplateStrengthExercise",
    "ProgramTemplateDay",
    "ProgramTemplateWeek",
    "ProgramTemplateKey",
    "ProgramTemplateTags",
)


class ProgramTemplateStrengthExercise(spice_rack.pydantic_bases.AbstractValueModel):
    """a single exercise that is programmed for a given day on a given week"""
    exercise_key: _strength_exercise.StrengthExerciseKey = Field(
        description="the key of the exercise"
    )
    sets: list[_misc.PrescribedSet] = Field(description="the prescribed sets")
    note: str = Field(
        description="free-form text field available to specify any info you want to add.",
        default="no notes."
    )


class ProgramTemplateDay(spice_rack.pydantic_bases.AbstractValueModel):
    """a single day of stuff to do. This exists as part of a program template's week"""
    day: int = Field(description="the day relative to the week, starts at 1", ge=1)
    strength_exercises: list[ProgramTemplateStrengthExercise] = Field(
        description="the prescribed list of strength exercises"
    )


class ProgramTemplateWeek(spice_rack.pydantic_bases.AbstractValueModel):
    """a single week of templated days. This exists as part of a program template"""
    week: int = Field(description="the week number within the program.", ge=1)
    days: list[ProgramTemplateDay] = Field(
        description="the sequence of sessions to perform.",
        max_items=7
    )


class ProgramTemplateKey(spice_rack.AbstractSpecialStr):
    """key for a program template"""
    @classmethod
    def _format_str(cls, root_data: str) -> str:
        return root_data


class ProgramTemplateTags(spice_rack.enum_bases.StrEnum):
    """tags for a program template"""
    ...
