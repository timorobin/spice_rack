from __future__ import annotations
import tortoise as orm  # noqa

from liftz import _models
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

    @classmethod
    def from_obj(
            cls,
            user_id: _models.user.UserId,
            obj: _models.strength_exercise.StrengthExerciseDef
    ) -> StrengthExerciseRecord:
        return StrengthExerciseRecord(
            user_id=user_id,
            key=obj.key,
            description=obj.description,
        )
