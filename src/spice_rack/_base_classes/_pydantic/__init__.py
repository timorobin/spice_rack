"""
Standard base classes extending pydantic's BaseMode.
These help us control and define specific behavior we want via pydantic models.
Another main goal here is to ensure pydantic migrations are easy, especially going from v1 to v2.
"""
from spice_rack._base_classes._pydantic.value_model import *
