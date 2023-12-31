from __future__ import annotations
import typing as t
from pydantic import Field, PrivateAttr

import spice_rack
from liftz import _models, _persistance, _constants


__all__ = (
    "SetupService",
)


_FilePathT = str

_db_services = _persistance.services


class SetupService(spice_rack.pydantic_bases.AbstractValueModel):
    """
    add standard set of database stuff if it isn't there already
    """
    class Config:
        arbitrary_types_allowed = True

    db_engine: _persistance.EngineT
    system_manifest_fp: t.Optional[_FilePathT] = Field(
        description="the path to the yaml file, if it exists.",
        default=None
    )

    _loaded_manifest: t.Optional[_models.misc.SystemManifest] = PrivateAttr(default=None)

    def _post_init_setup(self) -> None:
        if self.system_manifest_fp:
            loaded_manifest = _models.misc.SystemManifest.load_from_file_path(
                self.system_manifest_fp
            )
            self._loaded_manifest = loaded_manifest  # noqa - this is ok bc private attr

    def call(self) -> None:
        # if we have a loaded manifest, we do the stuff
        if self._loaded_manifest:
            db_session = _persistance.start_session(self.db_engine)

            # todo: optimize these to do bulk transactions

            # load users
            for user_create in self._loaded_manifest.users:
                existing_user_maybe = _db_services.user.fetch_by_email_maybe(
                    session=db_session, email=user_create.email
                )
                if existing_user_maybe:
                    continue
                else:
                    user_obj = _models.user.User(
                        user_id=_models.user.UserId.generate(),
                        name=user_create.name,
                        email=user_create.email,
                        is_superuser=user_create.is_superuser,
                    )
                    _db_services.user.save_new_user(
                        session=db_session,
                        user_obj=user_obj,
                        password=user_create.password
                    )

            # load strength exercises
            for exercise_def in self._loaded_manifest.strength_exercises:
                existing_record_maybe = _db_services.strength_exercise.fetch_by_key_maybe(
                    key=exercise_def.key,
                    session=db_session,
                    user_id=_constants.SYSTEM_USER_ID
                )
                if existing_record_maybe:
                    continue
                else:
                    _db_services.strength_exercise.save_obj(
                        obj=exercise_def,
                        user_id=_constants.SYSTEM_USER_ID,
                        session=db_session
                    )

            # load templates
            for template_obj in self._loaded_manifest.program_templates:
                existing_template_maybe = _db_services.program_template.fetch_by_key_maybe(
                    user_id=_constants.SYSTEM_USER_ID,
                    session=db_session,
                    key=template_obj.key
                )
                if existing_template_maybe:
                    continue
                else:
                    _db_services.program_template.save_obj(
                        obj=template_obj,
                        user_id=_constants.SYSTEM_USER_ID,
                        session=db_session
                    )

            db_session.close()
