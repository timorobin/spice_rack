from __future__ import annotations
import typing as t
import pydantic
import pydantic_core

from spice_rack import _bases, _logging


__all__ = (
    "MutuallyExclusiveFieldsException",
    "MutuallyExclusiveFieldsValidator"
)


class _MutuallyExclusiveFieldsErrorInfo(_bases.exceptions.ErrorInfoBase):
    class_name: str = pydantic.Field(
        description="the name of the class we are validating"
    )
    field_in_group: t.List[str] = pydantic.Field(
        description="the list of all field names we are grouping together and enforcing to be mutually exclusive"
    )
    fields_missing: t.List[str] = pydantic.Field(description="fields specified to check, but not found on the model")
    fields_specified: t.List[str] = pydantic.Field(description="multiple fields specified, when only one should be")


class MutuallyExclusiveFieldsException(_bases.exceptions.CustomExceptionBase[_MutuallyExclusiveFieldsErrorInfo]):
    def __init__(
            self,
            detail: str,
            class_name: str,
            field_in_group: t.List[str],
            fields_missing: t.List[str],
            fields_specified: t.List[str],

    ):
        error_info = {
            "class_name": class_name,
            "field_in_group": field_in_group,
            "fields_missing": fields_missing,
            "fields_specified": fields_specified
        }
        super().__init__(detail=detail, error_info=error_info, extra_info=None, verbose=True)


class MutuallyExclusiveFieldsValidator:
    """validates the specified fields are mutually exclusive"""
    def __init__(
            self,
            field_names: t.List[str],
            model_cls: t.Optional[t.Type[pydantic.BaseModel]] = None,
            at_least_one: bool = True,
            check_field_names: bool = True
    ):
        self.field_names = field_names
        self.at_least_one = at_least_one
        self.check_field_names = check_field_names

        if model_cls:
            missing_field_names: t.List[str] = []
            for field_name in self.field_names:
                if field_name not in model_cls.model_fields:
                    missing_field_names.append(field_name)
            if self.check_field_names and missing_field_names:
                raise ValueError(
                    f"error setting up '{self.__class__.__name__}', the model class, "
                    f"'{model_cls.__name__}', is missing"
                    f" the following fields: {missing_field_names}"
                )
            else:
                _logging.Logger.get_logger().info(
                    f"'{self.__class__.__name__}' configured on the '{model_cls.__name__}' class "
                    f" but the following fields weren't found on the class: {missing_field_names}"
                )

    def validate_inst(self, model_inst: pydantic.BaseModel) -> pydantic.BaseModel:
        """
        performs the actual validation
        Args:
            model_inst: the instance we are validating

        Returns: the instance passed in, unchanged

        Raises:
            MutuallyExclusiveFieldsException: if we find an error. todo: add more info on why we'd raise an error
        """
        data_dict = model_inst.model_dump(
            mode="python", include=set(self.field_names)
        )

        missing_field_names: t.List[str] = []
        specified_field_names: t.List[str] = []

        for field_name in self.field_names:
            if field_name not in data_dict:
                missing_field_names.append(field_name)
            if data_dict.get(field_name) is not None:
                specified_field_names.append(field_name)

        if self.check_field_names and missing_field_names:
            raise MutuallyExclusiveFieldsException(
                detail="not every field in the specified field names was specified on the model",
                class_name=model_inst.__class__.__name__,
                fields_missing=missing_field_names,
                fields_specified=specified_field_names,
                field_in_group=self.field_names,
            )

        if self.at_least_one and not specified_field_names:
            raise MutuallyExclusiveFieldsException(
                detail="at least one of the fields in the group should be non-null. All were found to be null",
                class_name=model_inst.__class__.__name__,
                fields_missing=missing_field_names,
                fields_specified=specified_field_names,
                field_in_group=self.field_names,
            )

        if len(specified_field_names) > 1:
            raise MutuallyExclusiveFieldsException(
                detail="found values for more than one field in a group that is specified to be mutually exclusive",
                class_name=model_inst.__class__.__name__,
                fields_missing=missing_field_names,
                fields_specified=specified_field_names,
                field_in_group=self.field_names,
            )
        return model_inst

    def _get_func(self) -> pydantic.functional_validators.ModelAfterValidatorWithoutInfo:

        def func(model_inst: pydantic.BaseModel) -> pydantic.BaseModel:
            try:
                return self.validate_inst(model_inst)
            except MutuallyExclusiveFieldsException as e:
                raise e.as_pydantic_error()
            except Exception as e:
                raise e

        return func

    def __get_pydantic_core_schema__(
            self,
            __source: t.Any,
            __handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.CoreSchema:
        val_func = self._get_func()

        schema = __handler(__source)
        schema = pydantic_core.core_schema.no_info_after_validator_function(
            function=val_func,
            schema=schema
        )
        return schema
