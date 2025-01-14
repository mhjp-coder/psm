# This file contains the base page layout for the application.

# Local modules
from .sidebar import sidebar

# stdlib

# dependencies
import reflex as rx


def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    return rx.box(
        rx.hstack(
            # Left sidebar
            rx.box(
                sidebar(),
                position="sticky",
                top="0px",
            ),
            rx.box(
                child,
                margin_x="10rem",
                margin_top="4rem",
                margin_bottom="10rem",
                width="100%",
            ),
            width="100%",
        ),
        rx.box(
            rx.logo(class_name="footer-style"),
            width="100%",
            position="fixed",
            bottom="0px",
            bg_color=rx.color("accent", 3),
        ),
        font_family="Noto Sans",
        width="100vw",
        margin="-8px",
        bg_color=rx.color("accent", 2),
    )
