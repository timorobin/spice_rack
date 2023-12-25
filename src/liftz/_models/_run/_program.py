from __future__ import annotations

from spice_rack import pydantic_bases, timestamp
from liftz._models import _template, _misc, _record_mixin

class ExerciseExecution(pydantic_bases.AbstractValueModel):
    exercise_key: _template.ExerciseKey
    sets: list[_misc.SetInfo]


class ExerciseSetExecutionRecord(
    pydantic_bases.AbstractValueModel,
    _record_mixin.RecordMixin
):

    created_at: timestamp.Timestamp
    exercise_key: _template.ExerciseKey
    weight: float
    reps: int


class Exercise


class ExerciseExecutionRecord(pydantic_bases.AbstractValueModel, _record_mixin.RecordMixin):



class ProgramRunSession(pydantic_bases.AbstractValueModel):
    week: int
    day: int
    tasks:


class _ProgramRunCommon(pydantic_bases.AbstractValueModel):
    start_date: timestamp.Timestamp


