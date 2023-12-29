from __future__ import annotations
import typing as t
from sqlalchemy import orm, select

from liftz._persistance._types import UserIdT
from liftz._persistance._repos import _record_base

if t.TYPE_CHECKING:
    from liftz._persistance._engine_builder import SessionT


__all__ = (
    "UserRecord",
)


class UserRecord(_record_base.TableBase):
    id: orm.Mapped[int] = orm.mapped_column(
        doc="the row id",
        default=None,
        primary_key=True
    )
    user_id: orm.Mapped[UserIdT] = orm.mapped_column(
        doc="unique id for the user",
        unique=True,
        index=True
    )
    name: orm.Mapped[str] = orm.mapped_column(
        doc="name of the user"
    )
    email: orm.Mapped[str] = orm.mapped_column(
        doc="email of the user"
    )
    password: orm.Mapped[str] = orm.mapped_column(
        doc="hashed password of the user"
    )

    @classmethod
    def get_table_name(cls) -> str:
        return "users"

    @classmethod
    def fetch_by_user_id(cls, session: SessionT, user_id: UserIdT) -> UserRecord:
        stmt = select(UserRecord).where(
            UserRecord.user_id == user_id
        )
        res = list(session.execute(stmt))
        if res is None:
            raise ValueError(
                f"nothing found with the user id, '{user_id}'"
            )
        else:
            return res[0]
