from __future__ import annotations

from liftz import _persistance, _settings

__all__ = (
    "build_db_session",
)


def build_db_engine(
        # db_uri: str
) -> _persistance.EngineT:
    # todo: don't rebuild everytime
    settings = _settings.Settings.load()
    return _persistance.build_engine(settings.db_uri)


def build_db_session() -> _persistance.SessionT:
    engine = build_db_engine()
    return _persistance.start_session(engine)
