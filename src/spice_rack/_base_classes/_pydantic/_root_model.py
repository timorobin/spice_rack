from __future__ import annotations
from typing import TypeVar, Generic, Optional
from pydantic.generics import GenericModel

from spice_rack._base_classes._pydantic._common_methods_mixin import CommonMethods
from spice_rack import _misc


__all__ = (
    "RootModel",
)


RootTypeTV = TypeVar("RootTypeTV", )


class RootModel(GenericModel, Generic[RootTypeTV], CommonMethods):
    """implement some of the usefulness of root models in v2, but using v1"""

    class Config:
        frozen = True
        validate_assignment = True
        extra = "forbid"
    __root__: RootTypeTV

    def __init__(
            self,
            root_data: Optional[RootTypeTV] = _misc.empty.EMPTY,
            *,
            __root__: Optional[RootTypeTV] = _misc.empty.EMPTY,
    ):
        """
        custom init method for the root model. By specifying the root_data positional arg we
        can support positional initialization, making this class behave more like a subtype of
        its root type. See example.

        Args:
            root_data: the positional arg for the underlying data, either specify this or use
                __root_ kwarg

            __root__: the keyword-only argument for specifying the underlying data. This
                is the "pydantic" style way to initialize this type

        Raises:
            ValueError: If specify both the positional and keyword args for our underlying data,
                or if we specify neither, and there is not '_get_default_value' classmethod set
        """
        if root_data != _misc.empty.EMPTY and __root__ != _misc.empty.EMPTY:
            raise ValueError(
                f"positional init and keyword init for __root__ both passed in?, "
                f"\nroot_data: {root_data}\n__root__: {__root__}"
            )

        # the thing we pass into super().__init__
        pydantic_kwarg: RootTypeTV

        if root_data != _misc.empty.EMPTY:
            pydantic_kwarg = root_data

        # pydantic's internal '_enforce_dict_if_root' could give us
        #  `{"__root__": {}}` so we treat that as empty as well
        elif __root__ != _misc.empty.EMPTY and __root__ != {}:
            pydantic_kwarg = __root__

        else:
            pydantic_kwarg = self._get_default_value()

        super().__init__(__root__=pydantic_kwarg)

    @classmethod
    def _get_default_value(cls) -> RootTypeTV:
        raise ValueError(
            f"the '{cls.__name__}' class doesn't have a specified default value."
        )
