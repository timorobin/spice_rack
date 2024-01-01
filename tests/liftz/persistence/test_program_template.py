from __future__ import annotations

import pytest
from liftz import persistence, models, constants


@pytest.fixture(scope="module")
async def create_exercises() -> None:
    exercises = [
        models.strength_exercise.StrengthExerciseDef(
            key=models.strength_exercise.StrengthExerciseKey(
                "squat"
            ),
            description="a barbell back squat",
            tags=[models.strength_exercise.StrengthExerciseTags.LOWER]
        ),
        models.strength_exercise.StrengthExerciseDef(
            key=models.strength_exercise.StrengthExerciseKey(
                "bench"
            ),
            description="a barbell bench",
            tags=[models.strength_exercise.StrengthExerciseTags.UPPER]
        ),
    ]
    records = [
        persistence.repos.StrengthExerciseRecord.from_obj(
            user_id=constants.SYSTEM_USER_ID,
            obj=obj
        ) for obj in exercises
    ]
    await persistence.repos.StrengthExerciseRecord.bulk_create(
        records
    )
    yield
    for rec in await persistence.repos.StrengthExerciseRecord.all():
        await rec.delete()


async def test_create():
    program_template = models.program_template.ProgramTemplate(
        key=models.program_template.components.ProgramTemplateKey("test-template"),
        description="a template",
        weeks=[
            models.program_template.components.ProgramTemplateWeek(
                week=1,
                days=[
                    models.program_template.components.ProgramTemplateDay(
                        day=1,
                        strength_exercises=[
                            models.program_template.components.ProgramTemplateStrengthExercise(
                                exercise_key=models.strength_exercise.StrengthExerciseKey("squat"),
                                sets=[
                                    models.misc.PrescribedSet(
                                        weight=100,
                                        reps=10
                                    )
                                ]
                            )
                        ]
                    ),
                    models.program_template.components.ProgramTemplateDay(
                        day=1,
                        strength_exercises=[
                            models.program_template.components.ProgramTemplateStrengthExercise(
                                exercise_key=models.strength_exercise.StrengthExerciseKey("squat"),
                                sets=[
                                    models.misc.PrescribedSet(
                                        weight=100,
                                        reps=10
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
        ],
        tags=[]
    )
    program_record_key = await persistence.repos.ProgramTemplateRecord.save_template_obj(
        user_id=constants.SYSTEM_USER_ID,
        obj=program_template
    )

    new_obj = await persistence.repos.ProgramTemplateRecord.get(key=program_record_key)
    await new_obj.fetch_related("strength_sets")
    assert len(new_obj.strength_sets) == 2

