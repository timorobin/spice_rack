from __future__ import annotations
import tortoise as orm  # noqa

from liftz._persistance._types import UserIdT
from liftz._persistance._repos import _record_base
from liftz import _models


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

    email: str = orm.fields.CharField(max_length=255, index=True)
    """email of the user"""

    password: str = orm.fields.TextField()
    """hashed password of the user"""

    is_superuser: bool = orm.fields.BooleanField()
    """if the user is a superuser."""

    @classmethod
    def from_user(
            cls,
            user_obj: _models.user.User,
            password: str
    ) -> UserRecord:
        return UserRecord(
            name=user_obj.name,
            email=user_obj.email,
            is_superuser=user_obj.is_superuser,
            user_id=user_obj.user_id,
            password=password
        )
