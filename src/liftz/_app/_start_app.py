from __future__ import annotations

from liftz import _settings, _services, _persistance


def start_app():
    settings = _settings.Settings.load()
    if settings.system_manifest_fp is None:
        raise ValueError()

    db_engine = _persistance.build_engine(db_uri=settings.db_uri)
    _services.SetupService(
        db_engine=db_engine,
        system_manifest_fp=settings.system_manifest_fp
    ).call()

    from liftz import _constants
    a = _persistance.services.strength_exercise.fetch_all_for_user(
        user_id=_constants.SYSTEM_USER_ID,
        session=_persistance.start_session(db_engine)
    )
    from devtools import debug
    debug(a)
    raise ValueError()

    from liftz._app import _UI
    ui = _UI.make_ui()

    ui.run(
        storage_secret=settings.ui_storage_secret
    )


start_app()
