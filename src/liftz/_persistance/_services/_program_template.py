from __future__ import annotations
import typing as t
from sqlmodel import select

from liftz import _constants
from liftz._persistance import _repos, _types
from liftz._persistance._engine_builder import SessionT
from liftz import _models

__all__ = (
    "fetch_all_for_user",
    "fetch_by_key_maybe",
    "save_obj"
)

_internal_repr = _models.program_template


def _record_to_obj(
        rec: _repos.ProgramTemplateRecord,
        session: SessionT
) -> _internal_repr.ProgramTemplate:
    raise NotImplementedError()


def fetch_all_for_user(
        session: SessionT,
        user_id: _types.UserIdT,
        specific_keys: t.Optional[list[_types.ProgramTemplateKeyT]] = None,
        include_system_records: bool = True
) -> list[_internal_repr.ProgramTemplate]:
    user_ids: list[_types.UserIdT] = [user_id]

    if include_system_records:
        user_ids.append(_constants.SYSTEM_USER_ID)

    user_ids = list(set(user_ids))

    _stmt = (
        select(_repos.ProgramTemplateRecord)
        .where(_repos.ProgramTemplateRecord.user_id.in_(user_ids))
    )
    if specific_keys:
        _stmt = _stmt.where(
            _repos.ProgramTemplateRecord.key.in_(specific_keys)
        )
    records = session.execute(_stmt).scalars().all()

    # sort records so user guid first.
    # if dupe keys, we drop the one for system user id.
    # this could happen if we change system assets after users have added their own
    records = sorted(
        records, key=lambda rec: rec.user_id == user_id
    )

    res: list[_internal_repr.ProgramTemplate] = []
    used_keys: set[_types.ProgramTemplateKeyT] = set()
    for rec_i in records:
        if rec_i.key in used_keys:
            continue
        else:
            res.append(_record_to_obj(rec_i, session=session))
            used_keys.add(rec_i.key)
    return res


def fetch_by_key_maybe(
        key: _types.ProgramTemplateKeyT,
        user_id: _types.UserIdT,
        session: SessionT,
        include_system_records: bool = True
) -> t.Optional[_internal_repr.ProgramTemplate]:
    user_ids: list[_types.UserIdT] = [user_id]

    if include_system_records:
        user_ids.append(_constants.SYSTEM_USER_ID)

    res = fetch_all_for_user(
        session=session,
        user_id=user_id,
        specific_keys=[key],
        include_system_records=include_system_records
    )
    if not res:
        return None
    else:
        return res[0]


def save_obj(
        obj: _internal_repr.ProgramTemplate,
        user_id: _types.UserIdT,
        session: SessionT,
) -> _types.ProgramTemplateKeyT:
    _existing_record_maybe = fetch_by_key_maybe(
        user_id=user_id, key=obj.key, session=session
    )
    if _existing_record_maybe:
        raise ValueError(
            f"a program template with the key, '{obj.key}', already exists "
        )
    else:
        raise NotImplementedError("a bunch of saving")
