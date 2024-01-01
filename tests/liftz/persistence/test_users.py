from __future__ import annotations

import pytest
from liftz import persistence, models


@pytest.mark.asyncio
async def test_create():
    user = models.user.User(
        user_id=models.user.UserId.generate(),
        name="John Doe",
        email="fake@gmail.com"
    )
    user_record = persistence.repos.UserRecord.from_user(
        user_obj=user, password="xyz"
    )
    await user_record.save()


async def test_fetch_by_email_found():
    found_user = await persistence.repos.UserRecord.get_or_none(
        email="fake@gmail.com"
    )
    assert found_user


async def test_fetch_by_email_not_found():
    not_found = await persistence.repos.UserRecord.get_or_none(
        email="non-existent@gmail.com"
    )
    assert not_found is None
