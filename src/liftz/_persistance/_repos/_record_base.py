from __future__ import annotations
from abc import abstractmethod
import typing as t
import tortoise as orm  # noqa


__all__ = (
    "TableBase",
)


class TableBase(orm.Model):
    """a baseclass for our tables"""
    id = orm.fields.IntField(
        description="the row id",
        default=None,
        primary_key=True
    )

    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        ...

    def __init_subclass__(cls, table=True, **kwargs):
        cls.Meta.table = cls.get_table_name()
        super().__init_subclass__()
