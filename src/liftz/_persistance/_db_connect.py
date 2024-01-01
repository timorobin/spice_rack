from __future__ import annotations

import tortoise as orm  # noqa
from liftz._persistance import _repos

# _MODULES = [
#     _repos.UserRecord,
#
#     _repos.StrengthExerciseRecord,
#
#     _repos.ProgramTemplateIndividualSet,
#     _repos.ProgramTemplateRecord
# ]


async def db_init(db_uri):
    await orm.Tortoise.init(
        db_url=db_uri, modules={_repos.REPO_MODULE_NAME: _repos}
    )
