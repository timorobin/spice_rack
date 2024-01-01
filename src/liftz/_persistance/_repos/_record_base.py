from __future__ import annotations
import typing as t

import tortoise as orm  # noqa


__all__ = (
    "TableBase",
    "REPO_MODULE_NAME"
)

REPO_MODULE_NAME = "models"  # tortoise app name
"""used when specifying foreign keys in tortoise orm"""


Self = t.TypeVar("Self", bound="TableBase")


class TableBase(orm.Model):
    """a baseclass for our tables"""
    class Meta:
        abstract = True

    id: int = orm.fields.IntField(pk=True, generated=True)
    """the row id"""

    # @classmethod
    # def find_one(cls: t.Type[Self], **kwargs) -> Self:
    #     return
