from __future__ import annotations

import sqlalchemy
from sqlalchemy import orm, engine

__all__ = (
    "build_engine",
    "EngineT",
    "start_session",
    "SessionT"
)


EngineT = engine.Engine
SessionT = orm.Session




def build_engine(db_uri: str = "") -> EngineT:
    return sqlalchemy.create_engine(
        db_uri, echo=True
    )


# class Session:
#     def __init__(self, db_engine: EngineT):
#         self._db_engine = db_engine
#         self._session = Session(db_engine)
#
#     @property
#     def sqlalchemy_session(self) -> SessionT:
#         return self._session
#
#     def close(self) -> None:
#         self._session.close()


def start_session(engine_obj: EngineT) -> SessionT:
    conn = engine_obj.connect()
    return sqlalchemy.orm.Session(conn)
