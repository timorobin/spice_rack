from __future__ import annotations
import tortoise as orm  # noqa


__all__ = (
    "TableBase",
    "REPO_MODULE_NAME"
)

REPO_MODULE_NAME = "_repos"
"""used when specifying foreign keys in tortoise orm"""


class TableBase(orm.Model):
    """a baseclass for our tables"""
    class Meta:
        abstract = True

    id: int = orm.fields.IntField(
        description="the row id",
        default=None,
        primary_key=True
    )
