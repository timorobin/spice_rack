from __future__ import annotations
from pydantic import Field

import spice_rack
from liftz._models import _misc, _strength_exercise, _


class CompletedStrengthExerciseSet(
    spice_rack.pydantic_bases.AbstractValueModel,
    spice_rack.timestamp.pydantic_mixins.CreatedAtMixin
):
    """a specific set of a strength exercise we completed"""
    exercise_key: _strength_exercise.StrengthExerciseKey = Field(
        description="the key of the exercise completed"
    )
    set_info: _misc.CompletedSet = Field(description="info on the set")


class CompletedProgramDay(
    spice_rack.pydantic_bases.AbstractValueModel,
):
    program_key: