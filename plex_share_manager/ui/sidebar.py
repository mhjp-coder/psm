# navigation components

# Local modules
from ..navigation import routes

# stdlib

# dependencies
import reflex as rx
from reflex.style import set_color_mode, color_mode


def dark_mode_toggle() -> rx.Component:
    return rx.segmented_control.root(
        rx.segmented_control.item(
            rx.icon(tag="monitor", size=20),
            value="system",
        ),
        rx.segmented_control.item(
            rx.icon(tag="sun", size=20),
            value="light",
        ),
        rx.segmented_control.item(
            rx.icon(tag="moon", size=20),
            value="dark",
        ),
        width="100%",
        align="center",
        style={
            "bg": rx.color("accent", 4),
            "color": rx.color("accent", 11),
            "border-radius": "0.5em",
        },
        on_change=set_color_mode,
        variant="classic",
        radius="large",
        value=color_mode,
    )


def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "0.5em",
            },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )


def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Dashboard", "database", routes.DASHBOARD_ROUTE),
        sidebar_item("Settings", "Settings", routes.SETTINGS_ROUTE),
        spacing="1",
        width="100%",
    )


def sidebar() -> rx.Component:
    return rx.fragment(
        rx.desktop_only(
            rx.vstack(
                rx.hstack(
                    rx.button(
                        rx.icon("user"),
                        size="3",
                        radius="full",
                    ),
                    rx.vstack(
                        rx.box(
                            rx.text(
                                "My account",
                                size="3",
                                weight="bold",
                            ),
                            rx.text(
                                "user@reflex.dev",
                                size="2",
                                weight="medium",
                            ),
                            width="100%",
                        ),
                        spacing="0",
                        justify="start",
                        width="100%",
                    ),
                    padding_x="0.5rem",
                    align="center",
                    width="100%",
                ),
                sidebar_items(),
                rx.spacer(),
                dark_mode_toggle(),
                spacing="5",
                min_height="100vh",
                padding_x="2em",
                padding_top="1.5em",
                padding_bottom="4.5em",
                bg=rx.color("accent", 3),
                align="start",
                width="16em",
            ),
        ),
        rx.mobile_and_tablet(
            rx.drawer.root(
                rx.drawer.trigger(rx.icon("align-justify", size=30)),
                rx.drawer.overlay(z_index="5"),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.vstack(
                            rx.box(
                                rx.drawer.close(rx.icon("x", size=30)),
                                width="100%",
                            ),
                            sidebar_items(),
                            rx.spacer(),
                            rx.vstack(
                                dark_mode_toggle(),
                                rx.divider(margin="0"),
                                rx.hstack(
                                    rx.button(
                                        rx.icon("user"),
                                        size="3",
                                        radius="full",
                                    ),
                                    rx.vstack(
                                        rx.box(
                                            rx.text(
                                                "My account",
                                                size="3",
                                                weight="bold",
                                            ),
                                            rx.text(
                                                "user@reflex.dev",
                                                size="2",
                                                weight="medium",
                                            ),
                                            width="100%",
                                        ),
                                        spacing="0",
                                        justify="start",
                                        width="100%",
                                    ),
                                    padding_x="0.5rem",
                                    align="center",
                                    justify="start",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="5",
                            ),
                            spacing="5",
                            width="100%",
                        ),
                        top="auto",
                        right="auto",
                        height="100%",
                        width="20em",
                        padding="1.5em",
                        bg=rx.color("accent", 2),
                    ),
                    width="100%",
                ),
                direction="left",
            ),
            padding="1em",
        ),
    )
