from __future__ import annotations

from liftz import _settings, _services, _persistance


def start_app():
    from liftz._app import _UI

    settings = _settings.Settings.load()
    if settings.system_manifest_fp is None:
        raise ValueError()

    db_engine = _persistance.build_engine(db_uri=settings.db_uri)
    _services.SetupService(
        db_engine=db_engine,
        system_manifest_fp=settings.system_manifest_fp
    ).call()
    _UI.ui.run(
        storage_secret=settings.ui_storage_secret
    )


start_app()
