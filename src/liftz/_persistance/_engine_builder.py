from __future__ import annotations

import sqlalchemy


__all__ = (
    "build_engine",
    "EngineT",
    "start_session",
    "SessionT"
)


EngineT = sqlalchemy.engine.Engine
SessionT = sqlalchemy.orm.Session


def build_engine(db_uri: str = "") -> EngineT:
    return sqlalchemy.create_engine(
        db_uri, echo=True
    )


def start_session(engine: EngineT) -> SessionT:
    conn = engine.connect()
    return sqlalchemy.orm.Session(conn)
