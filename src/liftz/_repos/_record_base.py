from __future__ import annotations
from abc import abstractmethod
from typing import Optional
from sqlmodel import SQLModel, Field

import spice_rack

__all__ = (
    "TableBase",
)


class TableBase(SQLModel):
    """a baseclass for our tables"""
    id: Optional[int] = Field(description="the row id", default=None, primary_key=True)

    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        ...

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(table=True)
        cls.__tablename__ = cls.get_table_name()
