# This is a template for a child page. It should be copied to a new file and modified as needed.

# Local modules
from ..ui import base_page

# stdlib

# dependencies
import reflex as rx


class State(rx.State):
    pass


def child_page() -> rx.Component:
    return base_page(rx.text("Copy Me!"))
