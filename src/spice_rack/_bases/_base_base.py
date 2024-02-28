from __future__ import annotations
import typing as t
import json
import abc

import pydantic


__all__ = (
    "BASE_MODEL_CONFIG",
    "CommonModelMethods"
)

BASE_MODEL_CONFIG = pydantic.ConfigDict(
    extra="forbid",
)


SelfTV = t.TypeVar("SelfTV", bound=pydantic.BaseModel)


class CommonModelMethods(abc.ABC):
    """a base model we use for all pydantic models, even the other bases"""
    def __iter__(self) -> t.Any:
        raise NotImplementedError(
            f"'{self.__class__.__name__}' doesn't have iteration implemented"
        )

    def json_dict(
            self,
            use_str_fallback: bool = False,
            **pydantic_kwargs
    ) -> dict:
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
        if use_str_fallback:
            fallback = str
        else:
            fallback = None

        pydantic_model_inst: pydantic.BaseModel = t.cast(
            pydantic.BaseModel, self
        )

        pydantic_model_inst.model_dump_json()
        dumped_json = pydantic_model_inst.__pydantic_serializer__.to_json(
            self,
            fallback=fallback,
            **pydantic_kwargs,
        )
        return json.loads(dumped_json)

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

    @classmethod
    def update_forward_refs(cls, **kwargs) -> None:
        """
        This extends pydantic's builtin hook for updating forward refs.
        We call our special '_import_forward_refs' hook to automatically bring in the things
        imported there, but also if you want to use it like pydantic, i.e. call it directly and
        provide your refs to update via kwargs, that is still supported.

        Returns:
            None: doesn't return anything, mutates the class calling this method

        Raises:
            NameError: pydantic raises a NameError if a forward ref is not accounted for
             in the kwargs
        """
        imported_refs = cls._import_forward_refs()
        kwargs.update(imported_refs)
        return super().update_forward_refs(**kwargs)  # type: ignore
