from __future__ import annotations
from abc import ABC

import spice_rack
from liftz import _models, _persistance


__all__ = (
    "ServiceBase",
)


class ServiceBase(spice_rack.api_helpers.ApiServiceBase, ABC):
    user_id: _models.user.UserId
    db_engine: _persistance.EngineT

    def get_db_session(self) -> _persistance.SessionT:
        return _persistance.start_session(engine=self.db_engine)

    def get_user(self) -> _models.user.User:
        return _persistance.repos.UserRecord.fetch_by_user_id(
            user_id=self.user_id, session=self.get_db_session()
        )

    def get_logger(self) -> spice_rack.LoggerT:
        return spice_rack.get_logger(specified_service_name=self.get_cls_name())
