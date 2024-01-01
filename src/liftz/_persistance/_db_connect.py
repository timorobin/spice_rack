from __future__ import annotations

import tortoise as orm  # noqa
from liftz._persistance import _repos

__all__ = (
    "db_init",
    "db_close"
)


async def db_init(db_uri):
    await orm.Tortoise.init(
        db_url=db_uri,
        modules={_repos.REPO_MODULE_NAME: [_repos]}
        # modules={"models": [_repos.TORTOISE_INIT_PATH]}
    )
    await orm.Tortoise.generate_schemas(safe=True)


async def db_close():
    await orm.Tortoise.close_connections()
