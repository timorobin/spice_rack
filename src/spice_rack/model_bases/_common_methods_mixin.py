from __future__ import annotations
from abc import ABC

from pydantic import BaseModel, Field

from strlt_common.utils import get_cls_name, pydantic_to_dict_json
from strlt_common.special_types.class_id_key import ClassIdKey

__all__ = ("PydanticBase",)


# following pydantic docs here:
#   https://docs.pydantic.dev/usage/exporting_models/#custom-json-deserialisation.
#  using orjson bc faster encoding/decoding and bc native datetime handling

class PydanticBase(BaseModel, ABC):
    """
    base for our pydantic classes
    """
    class Config:
        ...

    # model_config = ConfigDict(
    #     validate_default=True,
    #     defer_build=False
    # )

    # todo: remove this at some point, and any classes that actually use it can specify it
    #  explicitly in their own class definition
    extra: dict = Field(
        description="dict field where you can add extra info. "
                    "Can include any data types but everything must be json serializable",
        default_factory=dict
    )

    # @classmethod
    # def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
    #     for field_name, field_info in cls.__fields__.items():
    #         field_info.annotation = update_annotation(field_info.annotation)
    #         cls.__fields__[field_name] = field_info
    #     cls.model_rebuild(force=True, raise_errors=False)
    #     return

    @classmethod
    def get_cls_name(cls) -> str:
        return get_cls_name(cls=cls)

    @classmethod
    def get_cls_key(cls) -> ClassIdKey:
        return ClassIdKey(cls.get_cls_name())

    def json_dict(self, use_str_fallback: bool = False, **pydantic_kwargs) -> dict:
        return pydantic_to_dict_json(
            self,
            use_str_fallback=use_str_fallback,
            pydantic_kwargs=pydantic_kwargs
        )

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

    def _init_private_attributes(self) -> None:
        """
        Pydantic-provided hook that is called immediately after initialization.
        Unless a special situation, you should be overwriting our specified hooks rather than the
        pydantic one, so we're not tied to a pydantic api.

        Our hooks: "_post_init_setup" and "_post_init_validation"
        """
        super()._init_private_attributes()
        self._post_init_setup()
        self._post_init_validation()

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
        return super().update_forward_refs(**kwargs)

    @classmethod
    def update_forward_ref_all_children(cls, **kwargs) -> None:
        """
        This applies pydantic's builtin hook for updating forward refs to all subclasses
        of the calling class. Any kwargs specified here will be propagated to each subsequent
        `update_forward_refs` call.

        This also calls update_forward_refs on itself too.

        Returns:
            None: doesn't return anything, mutates the class calling this method and all of its
                subclasses

        Raises:
            NameError: pydantic raises a NameError if a forward ref is not accounted for
             in the kwargs
        """
        cls.update_forward_refs(**kwargs)

        for sub_cls in cls.__subclasses__():
            sub_cls.update_forward_refs(**kwargs)
