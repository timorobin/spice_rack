from __future__ import annotations
import typing as t
import pydantic


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

    @classmethod
    def get_cls_name(cls) -> str:
        return cls.__name__

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
            use_str_fallback: bool = True,
            **pydantic_kwargs
    ) -> t.Any:
        """
        convert into a json-encodeable data structure. whatever is encodeable version
        of RootTV, so if a list[str], this will return list of strings,
        if a pydantic model, this will return a dict.
        """
        pydantic_kwargs = pydantic_kwargs if pydantic_kwargs is not None else {}
        if use_str_fallback:
            fallback = str
        else:
            fallback = None
        return self.__pydantic_serializer__.to_python(
            self,
            mode="json",
            fallback=fallback,
            **pydantic_kwargs,
        )

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
    def model_rebuild(
            cls,
            *,
            force: bool = False,
            raise_errors: bool = True,
            _parent_namespace_depth: int = 2,
            _types_namespace: dict[str, t.Any] | None = None,
    ) -> None:
        """
        This extends pydantic's builtin hook for updating forward refs.
        We call our special '_import_forward_refs' hook to automatically bring in the things
        imported there, but also if you want to use it like pydantic, i.e. call it directly and
        provide your refs to update via kwargs, that is still supported.
        """
        _types_namespace_dict: dict[str, t.Any] = _types_namespace if _types_namespace else {}
        imported_refs = cls._import_forward_refs()
        _types_namespace_dict.update(imported_refs)
        return super().model_rebuild(
            force=force,
            raise_errors=raise_errors,
            _types_namespace=_types_namespace_dict,
            _parent_namespace_depth=_parent_namespace_depth
        )  # type: ignore
