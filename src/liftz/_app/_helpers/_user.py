from __future__ import annotations
import typing as t

from liftz import _persistance, _models
from liftz._app import _helpers

if t.TYPE_CHECKING:
    from nicegui.app import App


__all__ = (
    "user_creds_check",
    "get_user_id",
    "set_user_id"
)


# todo: remove this once we have proper auth

def user_creds_check(email: str, password: str) -> t.Optional[_models.user.UserId]:
    session = _helpers.build_db_session()
    user_maybe = _persistance.services.user.fetch_record_by_email_maybe(
        session=session,
        email=email
    )
    if user_maybe is None:
        return None
    else:
        if user_maybe.password == password:
            return user_maybe.user_id
        else:
            return None


def set_user_id(user_id: _models.user.UserId, app: App) -> None:
    app.storage.user["user_id"] = user_id


def get_user_id(app: App) -> _models.user.UserId:
    return app.storage.user.get("user_id")
