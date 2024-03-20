from __future__ import annotations
from typing import Any, Type, TypeVar


__all__ = (
    "check_type",
    "check_subclass",
    "is_subclass_strict",
)


_TypeClsTV = TypeVar("_TypeClsTV", )


def check_type(obj: Any, cls: Type[_TypeClsTV]) -> _TypeClsTV:
    if isinstance(obj, cls):
        return obj
    else:
        raise TypeError(
            f"expected obj to be type '{cls.__name__}' but encountered {obj.__class__.__name__}"
        )


def check_subclass(
        cls_in_question: Type[Any],
        cls_to_enforce: Type[_TypeClsTV]
) -> Type[_TypeClsTV]:
    if not isinstance(cls_in_question, type):
        raise TypeError(
            f"cls_in_question param is not even a class. it must be. "
            f"encountered: {cls_in_question} "
            f"which is type: '{cls_in_question.__class__.__name__}'"
        )
    if issubclass(cls_in_question, cls_to_enforce):
        return cls_in_question
    else:
        raise TypeError(
            f"expected obj to be subclass of '{cls_to_enforce.__name__}' "
            f"but encountered {cls_in_question.__class__.__name__} which isn't"
        )


def is_subclass_strict(child_cls: type, parent_cls: type) -> bool:
    """
    checks if the child class inherits from the parent class
    but is not the parent class exactly
    """
    if child_cls == parent_cls:
        return False
    return issubclass(child_cls, parent_cls)
