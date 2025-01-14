# This file contains the theme for the application

# Local modules

# stdlib

# dependencies
import reflex as rx


def base_theme() -> rx.Component:
    return rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        accent_color="indigo",
        gray_color="mauve",
    )
