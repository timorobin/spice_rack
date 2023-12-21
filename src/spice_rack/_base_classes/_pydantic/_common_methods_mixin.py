from __future__ import annotations
from abc import ABC
from typing import Type, Any
import json

from pydantic import BaseModel

from spice_rack._base_classes._pydantic import _misc


__all__ = ("CommonMethods",)


# following pydantic docs here:
#   https://docs.pydantic.dev/usage/exporting_models/#custom-json-deserialisation.
#  using orjson bc faster encoding/decoding and bc native datetime handling

class CommonMethods(_misc.ClassNameMixin, ABC):
    """
    adds common methods we apply to our bases that inherit from pydantic's BaseModel
    """

    def json_dict(self: BaseModel, use_str_fallback: bool = False, **pydantic_kwargs) -> dict:
        """
        Converts a pydantic instance to a dict, going through json first.
        This is a convenience function for when you want a dict, but want to use the json
        encoders connected to the pydantic object.

        Args:
            use_str_fallback: if true, we cast anything we cannot encode to a string
            **pydantic_kwargs: any kwargs available for pydantic's json method. see their docs

        Returns:
            dict: a natively json-encodable dict

        Notes:
            If the obj is a RootModel, calling `obj.json` would not necessarily return a dict,
            so we convert it to the form, `{"__root__": data}` to align with how pydantic
            would return `obj.dict()` in this scenario.

        Examples:
            simple class with custom date encoder::

                class Data(PydanticBase):
                    class Config:
                        json_encoders = {
                            dt.date: lambda date_obj: date_obj.strftime("%d/%m/%Y")
                        }
                    x: int
                    date: dt.date

                inst = Data(x=1, date=dt.date(year=2023, month=1, day=1))

                # regular dict
                inst.dict() == {"x": 1, "date": dt.date(year=2023, month=1, day=1)}

                # this method
                inst.json_dict() == {"x": 1, "date": "01/01/2023"}
                # note that the date is the json encoding tied to the encoder for this pydantic
                # class. I just used a familiar string format, it could be whatever is specified
        """
        pydantic_kwargs = pydantic_kwargs if pydantic_kwargs is not None else {}
        encoder_func = _EncoderMaybeFallback(
            pydantic_cls=type(self),
            use_str_fallback=use_str_fallback
        )
        obj_data = json.loads(self.json(encoder=encoder_func, **pydantic_kwargs))

        if "__root__" in self.__fields__:
            res = {"__root__": obj_data}
        else:
            res = obj_data

        if not isinstance(res, dict):
            raise ValueError(
                f"result is expected to be a dict, encountered type '{type(res)}'"
            )

        return res

    def _post_init_setup(self) -> None:
        """
        Hook for adding logic to execute immediately after initialization of this class.
        If you want to modify behavior, overwrite this method.

        Notes:
            - This is called after executing the pydantic _init_private_attributes, so any
              default factories or default values should be set on private attributes.
            - This called before '_post_init_validation'
        """
        return

    def _post_init_validation(self) -> None:
        """
        hook available for validating a class instance, after the instance has been initialized,
        all other validation has already finished. In pydantic v2, this would be equivalent to
        the decorator "@model_validator(mode="after") which is also an instance method, not
        classmethod, in contrast to the v1 analogue, "@root_validator(pre=True)" which is
        still a classmethod, even though everything is validated.

        Notes:
            - This is called after "_post_init_setup"

        """
        ...

    def __iter__(self):
        """
        We block attempts to iterate by default bc more often than not, if you end up iterating
        over an instance of one of our objects directly, without having implemented an
        iter dunder, it is unintentional and a mistake.

        If you do want a subclass to support iteration, overwrite this dunder.
        """
        raise ValueError(f"iteration not implemented for the '{self.get_cls_name()}' class")

    @classmethod
    def _import_forward_refs(cls) -> dict:
        """
        hook provided for convenience when you define a subclass with forward refs,
        to avoid circular import issue. Overwrite this method to do the imports and
        add the newly imported objects to a dict.

        Notes:
            - If you're not sure what to import and what keys to use, look at the stuff
              in the `if TYPE_CHECKING:` block, paste those exact imports in here and
              set them equal to their variable name within your current module's context.

        Returns:
            dict: a dict of references to update

        """
        return {}
    #
    # def _init_private_attributes(self) -> None:
    #     """
    #     Pydantic-provided hook that is called immediately after initialization.
    #     Unless a special situation, you should be overwriting our specified hooks rather than the
    #     pydantic one, so we're not tied to a pydantic api.
    #
    #     Our hooks: "_post_init_setup" and "_post_init_validation"
    #     """
    #     super()._init_private_attributes()
    #     self._post_init_setup()
    #     self._post_init_validation()
    #
    # @classmethod
    # def update_forward_refs(cls, **kwargs) -> None:
    #     """
    #     This extends pydantic's builtin hook for updating forward refs.
    #     We call our special '_import_forward_refs' hook to automatically bring in the things
    #     imported there, but also if you want to use it like pydantic, i.e. call it directly and
    #     provide your refs to update via kwargs, that is still supported.
    #
    #     Returns:
    #         None: doesn't return anything, mutates the class calling this method
    #
    #     Raises:
    #         NameError: pydantic raises a NameError if a forward ref is not accounted for
    #          in the kwargs
    #     """
    #     imported_refs = cls._import_forward_refs()
    #     kwargs.update(imported_refs)
    #     return super().update_forward_refs(**kwargs)
    #
    # @classmethod
    # def update_forward_ref_all_children(cls, **kwargs) -> None:
    #     """
    #     This applies pydantic's builtin hook for updating forward refs to all subclasses
    #     of the calling class. Any kwargs specified here will be propagated to each subsequent
    #     `update_forward_refs` call.
    #
    #     This also calls update_forward_refs on itself too.
    #
    #     Returns:
    #         None: doesn't return anything, mutates the class calling this method and all of its
    #             subclasses
    #
    #     Raises:
    #         NameError: pydantic raises a NameError if a forward ref is not accounted for
    #          in the kwargs
    #     """
    #     cls.update_forward_refs(**kwargs)
    #
    #     for sub_cls in cls.__subclasses__():
    #         sub_cls.update_forward_refs(**kwargs)


class _EncoderMaybeFallback:
    def __init__(self, pydantic_cls: Type[BaseModel], use_str_fallback: bool):
        self.pydantic_cls = pydantic_cls
        self.use_str_fallback = use_str_fallback

    def __call__(self, x: Any) -> Any:
        try:
            return self.pydantic_cls.__json_encoder__(x)

        except Exception as e:
            if self.use_str_fallback:
                return str(x)
            else:
                raise e
