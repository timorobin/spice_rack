"""
bases that subclass standard python types, to add some special behavior, or at least indicate
to the type checker, and IDE, that we are specifically expecting this type of thing.

For Example: we can make SpecialKey class that is a subclass of str and behaves exactly like it,
but when we define a db lookup method that expects SpecialKey, our IDE will tell us if we are
accidentally passing in a random string, not something we guarantee
to be an instance of SpecialKey
"""
from spice_rack._base_classes._special_types import (
    _special_type_mixin as special_type_mixin,
    _special_str_base as special_str_base,
)
