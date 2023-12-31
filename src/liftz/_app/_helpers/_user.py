from __future__ import annotations
import typing as t

from liftz import _persistance, _models
from liftz._app import _helpers

if t.TYPE_CHECKING:
    from nicegui.app import App


__all__ = (
    "user_creds_check",
    "get_current_user",
    "set_current_user",
    "get_authorization_status",
    "set_authorization_status"
)


# todo: remove this once we have proper auth

def user_creds_check(email: str, password: str) -> t.Optional[_models.user.User]:
    session = _helpers.build_db_session()
    user_maybe = _persistance.services.user.fetch_record_by_email_maybe(
        session=session,
        email=email
    )
    if user_maybe is None:
        return None
    else:
        if user_maybe.password == password:
            # todo: double db call
            return _persistance.services.user.fetch_by_user_id(
                user_id=user_maybe.user_id,
                session=session
            )
        else:
            return None


def set_current_user(user_obj: _models.user.User, app: App) -> None:
    app.storage.user["user"] = user_obj


def get_current_user(app: App) -> _models.user.User:
    return app.storage.user.get("user")


def get_authorization_status(app: App) -> bool:
    return app.storage.user.get("authenticated", False)


def set_authorization_status(app: App, status: bool) -> None:
    app.storage.user["authenticated"] = status
