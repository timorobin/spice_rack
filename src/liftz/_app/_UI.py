from __future__ import annotations
import typing as t

from liftz._app import _pages


__all__ = (
    "make_ui",
)


def make_ui() -> t.Any:
    from nicegui import ui
    _pages.register_login_page()
    return ui
