from __future__ import annotations

import pytest
from liftz import persistence, models, constants


@pytest.mark.asyncio
async def test_create():
    exercise_obj = models.strength_exercise.StrengthExerciseDef(
        key=models.strength_exercise.StrengthExerciseKey("squat"),
        description="a squat",
        tags=[models.strength_exercise.StrengthExerciseTags.UPPER]
    )

    record = persistence.repos.StrengthExerciseRecord.from_obj(
        obj=exercise_obj, user_id=constants.SYSTEM_USER_ID
    )
    await record.save()


async def test_fetch_by_key():
    found_record = await persistence.repos.StrengthExerciseRecord.get_or_none(
        key="squat"
    )
    assert found_record


async def test_fetch_by_email_not_found():
    not_found = await persistence.repos.StrengthExerciseRecord.get_or_none(
        key="unknown"
    )
    assert not_found is None
