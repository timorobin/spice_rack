from __future__ import annotations

from spice_rack import _base_classes


class ScenarioBase(_base_classes.pydantic.AbstractValueModel):
    """can use as a convenient base for our scenarios but not necessary"""
    name: str

    def __repr__(self) -> str:
        return self.name


# todo: make parameterization decorator using the pytest extension
