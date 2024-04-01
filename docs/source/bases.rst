=====
Bases
=====
This package contains base classes you can use to create classes with common functionality.

Base Base
---------
Common bases used by other base classes

.. autoclass:: spice_rack._bases._base_base.PydanticBase
   :special-members: __iter__
   :members: _post_init_setup, _post_init_validation, _pydantic_post_init_val_hook, json_dict, _import_forward_refs, update_forward_refs

Dispatchable Bases
------------------
Base classes that help you create a group of polymorphic pydantic classes with hooks
to create pydantic types that build a dispatched union json schema and parse correctly

.. autopydantic_model:: spice_rack._bases._dispatchable.DispatchedModelMixin
   :special-members: __init_subclass__
   :members: get_class_type, get_class_id, is_concrete, iter_concrete_subclasses, build_dispatched_ann, build_dispatcher_type_adapter
   :model-show-json: False

.. autopydantic_model:: spice_rack._bases._dispatchable.DispatchableValueModelBase
   :special-members: __init_subclass__
   :model-show-json: False

.. autopydantic_model:: spice_rack._bases._dispatchable.DispatchedClassContainer
   :members:
   :model-show-json: False

Settings
---------
subclasses pydantic_settings' base class to allow us to customize behavior.

.. autopydantic_settings:: spice_rack._bases._settings.SettingsBase
   :members:

Exceptions
----------
Standardized why to specify custom errors that include pydantic classes as error info
payloads. These play nice with our loggers especially, but in general output pretty formatted
structured error messages.

.. automodule:: spice_rack._bases._exception._exception_base
   :members:
.. automodule:: spice_rack._bases._exception._error_info
   :members:
.. automodule:: spice_rack._bases._exception._external_wrapper
   :members:
.. automodule:: spice_rack._bases._exception._exception_exception
   :members:

Special Str
-----------
.. autoclass:: spice_rack._bases._special_str.SpecialStrBase
   :members: _parse_non_str, _format_str_val, _validate_str_val, special_repr
