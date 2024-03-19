from __future__ import annotations
import datetime as dt
import pydantic

from spice_rack._bases._mixins._mixin_base import PydanticMixinBase


__all__ = ("CreatedAtMixin", "UpdatedAtMixin", "CreatedAtUpdatedAtMixin")


def _get_current_utc_datetime() -> dt.datetime:
    return dt.datetime.utcnow()


class CreatedAtMixin(PydanticMixinBase):
    """
    adds a datetime field, 'created_at' that can be timezone aware or naive
    """
    created_at: dt.datetime = pydantic.Field(
        description="timestamp the object was created at",
        default_factory=_get_current_utc_datetime
    )

    @pydantic.field_serializer("created_at", when_used="json-unless-none", check_fields=True)
    def _use_iso_for_created_at(self, data: dt.datetime):
        return data.isoformat()

    @property
    def created_at_str(self) -> str:
        return self.created_at.isoformat()


class UpdatedAtMixin(PydanticMixinBase):
    """
    adds a datetime field, 'updated_at' that can be timezone aware or naive
    """
    updated_at: dt.datetime = pydantic.Field(
        description="timestamp the object was last updated",
        default_factory=_get_current_utc_datetime
    )

    @pydantic.field_serializer("updated_at", when_used="json-unless-none", check_fields=True)
    def _use_iso_for_updated_at(self, data: dt.datetime):
        return data.isoformat()

    @property
    def updated_at_str(self) -> str:
        return self.updated_at.isoformat()


class CreatedAtUpdatedAtMixin(CreatedAtMixin, UpdatedAtMixin):
    """
    adds 2 datetime fields, 'created_at' and 'updated_at' that can be timezone aware or naive
    """
    ...
