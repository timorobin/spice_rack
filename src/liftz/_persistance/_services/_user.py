from __future__ import annotations
import typing as t
from sqlalchemy import select

from liftz._persistance import _repos
from liftz._persistance._engine_builder import SessionT
from liftz import _models


__all__ = (
    "user_record_to_obj",
    "fetch_by_user_id",
    "fetch_record_by_email_maybe",
    "fetch_by_email_maybe",
    "save_new_user"
)


def user_record_to_obj(user_rec: _repos.UserRecord) -> _models.user.User:
    """maps db record to internal object"""
    return _models.user.User(
        user_id=user_rec.user_id,
        email=user_rec.email,
        name=user_rec.name,
        is_superuser=user_rec.is_superuser
    )


def fetch_by_user_id(
        session: SessionT,
        user_id: _models.user.UserId
) -> _models.user.User:
    """
    fetch the user given the user ID.
    Args:
        session: db session
        user_id: id we are fetching

    Returns:
        User: internal user representation

    Raises:

        # todo: create custom error
        ValueError: nothing found for the ID
    """
    stmt = select(_repos.UserRecord).where(
        _repos.UserRecord.user_id == user_id
    )
    res = session.execute(stmt).scalar_one_or_none()
    if not res:
        raise ValueError(
            f"nothing found with the user id, '{user_id}'"
        )
    else:
        record_obj = res
        return user_record_to_obj(record_obj)


def fetch_record_by_email_maybe(
        session: SessionT, email: str
) -> t.Optional[_repos.UserRecord]:
    stmt = select(_repos.UserRecord).where(
        _repos.UserRecord.email == email
    )
    res = session.execute(stmt).scalar_one_or_none()

    if not res:
        return None
    else:
        record_obj = res
        return record_obj


def fetch_by_email_maybe(
        session: SessionT, email: str
) -> t.Optional[_models.user.User]:
    stmt = select(_repos.UserRecord).where(
        _repos.UserRecord.email == email
    )
    res = session.execute(stmt).scalar_one_or_none()

    if not res:
        return None
    else:
        record_obj = res
        return user_record_to_obj(record_obj)


# todo: update when we fix our user stuff
def save_new_user(
        session: SessionT,
        user_obj: _models.user.User,
        password: str
) -> None:
    record = _repos.UserRecord(
        user_id=_models.user.UserId.generate(),
        name=user_obj.name,
        email=user_obj.email,
        is_superuser=user_obj.is_superuser,
        password=password,
    )
    session.add(record)
    session.commit()
