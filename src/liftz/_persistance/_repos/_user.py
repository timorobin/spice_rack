from __future__ import annotations
import tortoise as orm  # noqa

from liftz._persistance._types import UserIdT
from liftz._persistance._repos import _record_base


__all__ = (
    "UserRecord",
)


class UserRecord(_record_base.TableBase):
    class Meta:
        table = "users"

    user_id: UserIdT = orm.fields.UUIDField(
        unique=True,
        index=True
    )
    """unique id for the user"""

    name: str = orm.fields.TextField()
    """name of the user"""

    email: str = orm.fields.TextField(index=True)
    """email of the user"""

    password: str = orm.fields.TextField()
    """hashed password of the user"""

    is_superuser: bool = orm.fields.BooleanField()
    """if the user is a superuser."""
