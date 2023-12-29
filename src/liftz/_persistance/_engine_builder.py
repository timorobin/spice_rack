from __future__ import annotations

import sqlalchemy


__all__ = (
    "build_engine",
)


def build_engine(db_uri: str = "") -> sqlalchemy.engine.Engine:
    return sqlalchemy.create_engine(
        db_uri, echo=True
    )
