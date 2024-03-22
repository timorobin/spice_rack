from __future__ import annotations
import typing as t
import pydantic
import json


__all__ = (
    "RootModel",
)


RootTV = t.TypeVar("RootTV", )
SelfTV = t.TypeVar("SelfTV", bound="RootModel")


class RootModel(pydantic.RootModel[RootTV], t.Generic[RootTV]):
    """subclass pydantic's RootModel"""

    @classmethod
    def _get_default_value(cls) -> RootTV:
        raise ValueError(
            f"'{cls.__name__}' doesn't have a '_get_default_value' implemented so you must "
            f"specify the value, there is no default"
        )

    @pydantic.model_validator(mode="before")
    def _use_default(cls, data: t.Any) -> t.Any:
        if data is pydantic.fields.PydanticUndefined:
            return cls._get_default_value()
        else:
            return data

    def __iter__(self):
        """
        We block attempts to iterate by default bc more often than not, if you end up iterating
        over an instance of one of our objects directly, without having implemented an
        iter dunder, it is unintentional and a mistake.

        If you do want a subclass to support iteration, overwrite this dunder.
        """
        raise ValueError(f"iteration not implemented for the '{self.get_cls_name()}' class")

    def _post_init_setup(self) -> None:
        """
        Overwrite this hook to set perform misc. logic before calling _post_init_validation.
        Common use case for this is initializing private attributes.
        Notes: Make sure to call super()._post_init_setup
        """
        return

    def _post_init_validation(self) -> None:
        """
        Overwrite this hook to set perform misc. validation logic on the instance, after
        all other validators have been executed.
        This is also called after the '_post_init_setup' hook is called
        Notes: Make sure to call super()._post_init_validation
        """
        return

    @pydantic.model_validator(mode="after")
    def _pydantic_post_init_val_hook(self: SelfTV) -> SelfTV:
        """
        Pydantic's hook that gets executed after we initialize an instance.
        rather than overwrite this, overwrite the '_post_init_setup' and '_post_init_validation'
        hooks
        """
        self._post_init_setup()
        self._post_init_validation()
        return self

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