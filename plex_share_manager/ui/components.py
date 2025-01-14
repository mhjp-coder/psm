# This file contains the components used in the UI.

# Local modules

# stdlib

# dependencies
import reflex as rx


def _badge(icon: str, text: str, color_scheme: str):
    return rx.badge(
        rx.icon(icon, size=20),
        text,
        color_scheme=color_scheme,
        radius="full",
        variant="surface",
        size="3",
        min_width="115px",
        padding=".5rem",
        padding_x="1rem",
        wrap="wrap",
        spacing="2",
    )


def status_badge(status: str) -> rx.Component:
    badge_mapping = {
        "active": ("check", status, "jade"),
        "expiring": ("check", status, "amber"),
        "expired": ("ban", status, "crimson"),
        "never": ("star", status, "yellow"),
        "default": ("loader", "No info", "blue"),
    }
    return _badge(*badge_mapping.get(status, badge_mapping["default"]))


def form_input_field(
    label: str,
    type: str,
    name: str,
    icon: str,
    placeholder: str = "",
    default_value: str | bool = "",
    disabled: bool = False,
    is_required: bool = False,
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.hstack(
                rx.icon(icon, size=16),
                rx.form.label(label),
                align="center",
                spacing="2",
            ),
            rx.form.control(
                rx.input(
                    placeholder=placeholder,
                    type=type,
                    default_value=default_value,
                    disabled=disabled,
                    required=is_required,
                    size="3",
                    height=rx.match(
                        type,
                        ("date", "3rem"),
                        "",
                    ),
                ),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )


def not_editable_field(text: str, icon: str, field_name: str) -> rx.Component:
    return rx.flex(
        rx.hstack(
            rx.icon(icon, size=16),
            rx.text(field_name),
            align="center",
            spacing="2",
            padding_bottom="0.5rem",
        ),
        rx.box(
            rx.text(
                text | "N/A",
                size="3",
                padding_left=".25rem",
                color=rx.color("gray", 11),
            ),
            border_radius="10px",
            border="1px solid var(--gray-9)",
            padding="0.5rem",
        ),
        width="100%",
        direction="column",
        spacing="1",
    )


def form_switch_box(
    text: str,
    name: str,
    form_value: str,
    icon: str = "circle",
    display_icon: bool = False,
    selected: bool = False,
    disabled: bool = False,
    on_change: rx.EventHandler = None,
) -> rx.Component:
    """Creates a box component that represents a switch, works best in a grid layout even if only using one."""
    return rx.form.field(
        rx.flex(
            rx.hstack(
                rx.icon(
                    icon,
                    size=24,
                    color=rx.color("accent", 12),
                    style=rx.cond(not display_icon, {"display": "none"}, ""),
                ),
                rx.form.label(
                    text,
                    font_size="1rem",
                    white_space="nowrap",
                    color=rx.color("accent", 12),
                ),
                position="absolute",
                justify="center",
                align="center",
                width="100%",
                height="100%",
                pointer_events="none",
                spacing="1",
            ),
            rx.el.input(
                type="checkbox",
                default_checked=selected,
                name=name,
                id=name,
                value=form_value,
                disabled=disabled,
                on_change=on_change,
                appearance="none",
                background=rx.color("gray", 3),
                border="1px solid",
                border_color=rx.color("gray", 9),
                border_radius="10px",
                min_width="11.25rem",
                min_height="3rem",
                cursor="pointer",
                transition="all 0.2s ease-in-out",
                box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                _hover={"background": rx.color("gray", 4)},
                _checked={
                    "background": rx.color("accent", 4),
                    "border": "1px solid",
                    "border_color": rx.color("accent", 10),
                    ":hover": {"background": rx.color("accent", 5)},
                },
            ),
        ),
        position="relative",
    )
