=======
Logging
=======
Wrapper around loguru with some opinionated formatting. There are pydantic models for configuring the sinks,
and custom logger class that does some formatting for you and helps with structured data.


Main Logging Class
------------------
main interface to setup and use the logger.

.. autopydantic_model:: spice_rack._logging._logger.Logger
   :members:
