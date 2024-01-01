from __future__ import annotations
import tortoise as orm  # noqa
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

    strength_sets: orm.fields.ReverseRelation[ProgramTemplateIndividualSet]

    @classmethod
    def get_table_name(cls) -> str:
        return _TEMPLATE_TABLE_NAME


class ProgramTemplateIndividualSet(_record_base.TableBase):
    class Meta:
        table = _TEMPLATE_SET_TABLE_NAME

    user_id: UserIdT = orm.fields.UUIDField(index=True)
    """the id of the user connected to this record"""

    program_record_id: orm.fields.ForeignKeyRelation[ProgramTemplateRecord] = (
        orm.fields.ForeignKeyField(
            f"{_record_base.REPO_MODULE_NAME}.ProgramTemplateRecord",
            related_name="strength_sets", to_field="id"
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
