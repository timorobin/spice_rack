from __future__ import annotations
from typing import Optional
from pydantic import Field

import spice_rack
from liftz._models import _strength_exercise, _misc


__all__ = (
    "StrengthExerciseSetInProgress",
    "ProgramDayInProgress",
    "ProgramDayNotStartedExercise",
    "ProgramDayNotStarted",
    "ProgramDayFinishedExercise",
    "ProgramDayFinished"
)


class StrengthExerciseSetInProgress(spice_rack.pydantic_bases.AbstractValueModel):
    exercise_key: _strength_exercise.StrengthExerciseKey
    template_note_exercise_level: str
    user_note_exercise_level: str
    finished_at: spice_rack.timestamp.Timestamp
    weight_prescribed: float
    weight_used: Optional[float]
    reps_prescribed: int
    reps_completed: Optional[int]
    template_note_set_level: str
    user_note_set_level: str


class ProgramDayInProgress(spice_rack.pydantic_bases.AbstractValueModel):
    started_at: spice_rack.timestamp.Timestamp
    week: int
    day: int
    strength_exercises: list[StrengthExerciseSetInProgress]
    user_note: str


class ProgramDayNotStartedExercise(spice_rack.pydantic_bases.AbstractValueModel):
    """a single exercise that is programmed for a given day on a given week"""
    exercise_key: _strength_exercise.StrengthExerciseKey = Field(
        description="the key of the exercise"
    )
    sets: list[_misc.PrescribedSet] = Field(description="the prescribed sets")
    note: str = Field(
        description="free-form text field available to specify any info you want to add.",
        default="no notes."
    )


class ProgramDayNotStarted(spice_rack.pydantic_bases.AbstractValueModel):
    day: int = Field(description="the day relative to the week, starts at 1", ge=1)
    strength_exercises: list[ProgramDayNotStartedExercise] = Field(
        description="the prescribed list of strength exercises"
    )


class ProgramDayFinishedExercise(spice_rack.pydantic_bases.AbstractValueModel):
    exercise_key: _strength_exercise.StrengthExerciseKey
    template_note_exercise_level: str
    user_note_exercise_level: str
    finished_at: spice_rack.timestamp.Timestamp
    weight_prescribed: float
    weight_used: float
    reps_prescribed: int
    reps_completed: int
    template_note_set_level: str
    user_note_set_level: str


class ProgramDayFinished(spice_rack.pydantic_bases.AbstractValueModel):
    started_at: spice_rack.timestamp.Timestamp
    week: int
    day: int
    strength_exercises: list[ProgramDayFinishedExercise]
    user_note: str
    finished_at: spice_rack.timestamp.Timestamp
