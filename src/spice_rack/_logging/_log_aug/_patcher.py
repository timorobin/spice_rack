from __future__ import annotations
from typing import TYPE_CHECKING
from devtools import pformat

from spice_rack._logging._log_aug import _container

if TYPE_CHECKING:
    from loguru import Record


__all__ = (
    "log_augmentations_patcher",
)


def log_augmentations_patcher(record: Record) -> None:
    """
    look for the log augmentations in the 'extra' attribute of the loguru record object
    and ensure each item is are valid implementation of 'LogAugmentationProtocol'
    then reformat the extra record to contain correct info.

    This executes on a given log record prior to getting sent to the handlers.
    So handler specific formatters should contain the additional info added here.
    """
    extra = record.get("extra", {})

    log_augmentations = []
    for aug_raw in extra.pop("log_augmentations", []):
        aug_obj = _container.GeneralLogAugmentation.validate(aug_raw)
        serializable_data = aug_obj.get_serializable_data()
        if serializable_data:
            log_augmentations.append(aug_obj.get_serializable_data())
    if log_augmentations:
        extra["log_augmentations_dumped"] = pformat(log_augmentations)
    return
