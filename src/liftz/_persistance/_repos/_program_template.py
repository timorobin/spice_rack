from __future__ import annotations
import tortoise as orm  # noqa

from liftz import _models
from liftz._persistance._repos import _record_base
from liftz._persistance._types import (
    ProgramTemplateKeyT,
    StrengthExerciseKeyT,
    # ProgramTemplateTagsT,
    UserIdT
)

_TEMPLATE_TABLE_NAME = "program_templates"
_TEMPLATE_SET_TABLE_NAME = "individual_template_sets"


__all__ = (
    "ProgramTemplateRecord",
    "ProgramTemplateIndividualSet"
)


class ProgramTemplateRecord(_record_base.TableBase):
    class Meta:
        table = _TEMPLATE_TABLE_NAME

    user_id: UserIdT = orm.fields.UUIDField(index=True)
    """the id of the user connected to this record"""

    key: ProgramTemplateKeyT = orm.fields.CharField(index=True, max_length=255)
    """the key for this program template"""

    description: str = orm.fields.TextField()
    """free-form description for this exercise"""

    # todo: make a special string - see todo
    # tags: orm.Mapped[list[ProgramTemplateTagsT]] = Field(
    #     ARRAY(Enum),
    #     description="a list of tags tied to this program"
    # )

    strength_sets: orm.fields.ReverseRelation["ProgramTemplateIndividualSet"]

    @classmethod
    async def save_template_obj(
            cls,
            user_id: _models.user.UserId,
            obj: _models.program_template.ProgramTemplate
    ) -> _models.program_template.components.ProgramTemplateKey:
        program_record = ProgramTemplateRecord(
            user_id=user_id,
            key=obj.key,
            description=obj.description,
        )
        await program_record.save()

        set_records: list[ProgramTemplateIndividualSet] = []
        for week_obj in obj.weeks:
            week_num = week_obj.week
            for day_obj in week_obj.days:
                day_num = day_obj.day
                for strength_exercise_obj in day_obj.strength_exercises:

                    for ix in range(len(strength_exercise_obj.sets)):
                        set_obj_i = strength_exercise_obj.sets[ix]
                        set_record_i = ProgramTemplateIndividualSet(
                            user_id=user_id,
                            program_record_id=program_record,
                            exercise_key=strength_exercise_obj.exercise_key,
                            week=week_num,
                            day=day_num,
                            weight=set_obj_i.weight,
                            reps=set_obj_i.reps
                        )
                        set_records.append(set_record_i)

        await ProgramTemplateIndividualSet.bulk_create(set_records)
        return obj.key


class ProgramTemplateIndividualSet(_record_base.TableBase):
    class Meta:
        table = _TEMPLATE_SET_TABLE_NAME

    user_id: UserIdT = orm.fields.UUIDField(index=True)
    """the id of the user connected to this record"""

    program_record_id: orm.fields.ForeignKeyRelation[ProgramTemplateRecord] = (
        orm.fields.ForeignKeyField(
            model_name=f"{_record_base.REPO_MODULE_NAME}.ProgramTemplateRecord",
            related_name="strength_sets"
        )
    )

    exercise_key: StrengthExerciseKeyT = orm.fields.CharField(index=True, max_length=255)
    """the key for the exercise info"""

    week: int = orm.fields.IntField()
    """the week this set is from"""

    day: int = orm.fields.IntField()
    """the day this set is from"""

    weight: float = orm.fields.IntField()
    """the weight prescribed"""

    reps: int = orm.fields.IntField()
    """the reps prescribed"""
