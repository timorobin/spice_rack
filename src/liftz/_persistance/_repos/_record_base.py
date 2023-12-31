from __future__ import annotations
from abc import abstractmethod
import typing as t
from sqlmodel import SQLModel, Field

__all__ = (
    "TableBase",
)


class TableBase(SQLModel):
    """a baseclass for our tables"""
    id: t.Optional[int] = Field(
        description="the row id",
        default=None,
        primary_key=True
    )

    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        ...

    def __init_subclass__(cls, table=True, **kwargs):
        cls.__tablename__ = cls.get_table_name()
        super().__init_subclass__()
