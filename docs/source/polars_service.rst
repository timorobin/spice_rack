==============
Polars Service
==============
Polars DataFrame and LazyFrame type annotations meant to integrate with pydantic's validation system, meaning
I can set them as attributes on pydantic models without pydantic seeing them as 'arbitrary types'

Services
---------
.. automodule:: spice_rack._polars_service._services._joiner
   :members:

.. automodule:: spice_rack._polars_service._services._json_dumper
   :members:

.. automodule:: spice_rack._polars_service._services._misc
   :members:


Types
-----
type annotations and type adapters for polars classes

.. automodule:: spice_rack._polars_service._types._collected_df
   :members:

.. automodule:: spice_rack._polars_service._types._lazy_df
   :members:

.. automodule:: spice_rack._polars_service._types._maybe_lazy
   :members:

.. automodule:: spice_rack._polars_service._types._discrim_helper
   :members:
