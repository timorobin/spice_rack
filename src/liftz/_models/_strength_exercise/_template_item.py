from __future__ import annotations
from pydantic import Field

import spice_rack
from liftz._models import _record_mixin, _misc
from liftz._models._strength_exercise import (
    _key, _def
)


class ProgramTemplateStrengthExerciseItem(spice_rack.pydantic_bases.AbstractValueModel):
    """
    Specifies a strength exercise to perform and the sets.
    This lives within a program template's day.
    """
    exercise_key: _key.StrengthExerciseKey = Field(
        description="the key to the exercise definition"
    )
    sets: list[_misc.SetInfo] = Field(
        description="info about the sets to perform"
    )


class ProgramTemplateStrengthExerciseSetRecord(
    spice_rack.pydantic_bases.AbstractValueModel,
    _record_mixin.RecordMixin
):
    """record containing info about """