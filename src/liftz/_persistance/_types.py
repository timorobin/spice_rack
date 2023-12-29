from __future__ import annotations

from liftz import _models

__all__ = (
    "KeyT",
    "ExerciseTagsEnumT",
    "ProgramTemplateKeyT",
    "ProgramTemplateTagsT",
    "StrengthExerciseKeyT",
    "TimestampT",
    "UserIdT"

)

KeyT = str
ExerciseTagsEnumT = _models.strength_exercise.StrengthExerciseTags
ProgramTemplateKeyT = str  # _models.program_template.components.ProgramTemplateKey
ProgramTemplateTagsT = _models.program_template.components.ProgramTemplateTags
StrengthExerciseKeyT = str  # _models.strength_exercise.StrengthExerciseKey
TimestampT = int  # spice_rack.timestamp.Timestamp
UserIdT = str
