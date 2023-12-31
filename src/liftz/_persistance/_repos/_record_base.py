from __future__ import annotations
from abc import abstractmethod
from sqlalchemy import orm

__all__ = (
    "TableBase",
)


class TableBase(orm.DeclarativeBase):
    """a baseclass for our tables"""

    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        ...

    def __init_subclass__(cls, **kwargs):
        cls.__tablename__ = cls.get_table_name()
        super().__init_subclass__(**kwargs)
