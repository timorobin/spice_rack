from __future__ import annotations
import tortoise as orm  # noqa

from liftz._persistance._repos import _record_base
from liftz._persistance._types import (
    StrengthExerciseKeyT,
    UserIdT
)


__all__ = (
    "StrengthExerciseRecord",
)


class StrengthExerciseRecord(_record_base.TableBase):
    """record of strength exercises"""
    class Meta:
        table = "strength_exercises"

    user_id: UserIdT = orm.fields.UUIDField(index=True)
    """the id of the user connected to this record"""

    key: StrengthExerciseKeyT = orm.fields.CharField(index=True, max_length=255)
    """the key for this exercise"""

    description: str = orm.fields.TextField()
    """free-form description for this exercise"""

    # todo:  add back
    # tags: orm.Mapped[ExerciseTagsEnumT] = Field(
    #     ARRAY(Enum),
    #     description="list of tags for this exercise"
    # )
