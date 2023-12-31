from __future__ import annotations
from sqlmodel import Field

from liftz._persistance._types import UserIdT
from liftz._persistance._repos import _record_base


__all__ = (
    "UserRecord",
)


class UserRecord(_record_base.TableBase, table=True):
    user_id: UserIdT = Field(
        description="unique id for the user",
        unique=True,
        index=True
    )
    name: str = Field(
        description="name of the user"
    )
    email: str = Field(
        description="email of the user"
    )
    password: str = Field(
        description="hashed password of the user"
    )
    is_superuser: bool = Field(
        description="if the user is a superuser."
    )

    @classmethod
    def get_table_name(cls) -> str:
        return "users"
