# Main dashboard page for the application.

# Local modules
from ..ui import base_page, components
from ..models import User
from ..state import UserState, ImportState

# stdlib

# dependencies
import reflex as rx


def dashboard() -> rx.Component:
    """Create the main dashboard page."""
    return base_page(
        rx.box(
            rx.badge(
                rx.icon("database", size=28),
                rx.heading("User Dashboard", size="6"),
                radius="full",
                align="center",
                variant="outline",
                padding="1rem",
            ),
            rx.divider(margin_top="2rem"),
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.cond(
                            UserState.sort_reverse,
                            rx.icon(
                                "arrow-down-z-a",
                                size=32,
                                cursor="pointer",
                                align_self="center",
                                on_click=UserState.set_toggle_sort,
                            ),
                            rx.icon(
                                "arrow-down-a-z",
                                size=32,
                                cursor="pointer",
                                align_self="center",
                                on_click=UserState.set_toggle_sort,
                            ),
                        ),
                        rx.select(
                            UserState.sort_options,
                            placeholder="Sort By: ...",
                            on_change=UserState.set_sort_values,
                            size="3",
                            width="8.75rem",
                        ),
                        spacing="3",
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("search", size=20)),
                        on_change=UserState.set_filter_values,
                        font_size="1.25rem",
                        height="2.5rem",
                    ),
                    rx.hstack(
                        invite_user_dialog(),
                        plex_user_sync_dialog(),
                        plex_section_sync_dialog(),
                        spacing="3",
                    ),
                    margin_top="2.5rem",
                    margin_bottom="1.75rem",
                    spacing="6",
                ),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            column_header_cell("Avatar", "image"),
                            column_header_cell("Name", "user-round"),
                            column_header_cell("Email", "at-sign"),
                            column_header_cell("Plex Username", "circle-user-round"),
                            column_header_cell("Plex ID", "hash"),
                            column_header_cell("Expiry Date", "calendar-days"),
                            column_header_cell("Status", "circle-help"),
                            column_header_cell("Actions", "cog"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(UserState.all_users, create_table_row),
                    ),
                    variant="surface",
                    background=rx.color("accent", 3),
                    size="3",
                    align="center",
                ),
                align="center",
            ),
        )
    )


def column_header_cell(text: str, icon: str) -> rx.Component:
    """Create a table head cell with an text and icon."""
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            padding_y=".75rem",
            padding_x="1rem",
        ),
    )


def create_table_row(user: User) -> rx.Component:
    """Create a row for a user in the table."""
    return rx.table.row(
        rx.table.cell(
            rx.avatar(src=user.avatar_url, fallback=user.email[0]),
            align="center",
        ),
        rx.table.cell(user.name),
        rx.table.cell(user.email),
        rx.table.cell(user.username),
        rx.table.cell(user.plex_id),
        rx.table.cell(user.expiry_date.to(str)),
        rx.table.cell(
            rx.match(
                user.status.lower(),
                ("active", components.status_badge("active")),
                ("expiring", components.status_badge("expiring")),
                ("expired", components.status_badge("expired")),
                ("never", components.status_badge("never")),
                components.status_badge("default"),
            ),
            align="center",
        ),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    user.invite_pending,
                    uninvite_user_dialog(user),
                    rx.fragment(
                        update_user_dialog(user),
                        update_user_sections_dialog(user),
                        delete_users_dialog(user),
                    ),
                ),
                align="center",
                justify="center",
            ),
            align="center",
        ),
        _hover={"background": rx.color("accent", 4)},
    )


def invite_user_dialog() -> rx.Component:
    """Create a dialog for adding a user."""
    return rx.dialog.root(
        create_dialog_trigger("Invite User", "user-round-plus"),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="user-round-plus", size=34),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Add New user",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Fill the form with the user's info",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5rem",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        # Email
                        components.form_input_field(
                            label="Email",
                            placeholder="user@example.com",
                            type="email",
                            name="user_email",
                            icon="mail",
                            is_required=True,
                        ),
                        # Full Name
                        components.form_input_field(
                            label="Full Name",
                            placeholder="Full Name",
                            type="text",
                            name="user_name",
                            icon="user-round",
                        ),
                        rx.hstack(
                            # Expiry Date
                            components.form_input_field(
                                label="Expiry Date",
                                default_value="2025-01-01",
                                type="date",
                                name="user_expiry_date",
                                icon="calendar-days",
                            ),
                            # Status
                            components.form_switch_box(
                                text="Never Expire",
                                name="user_never_expire",
                                form_value=True,
                                icon="star",
                                display_icon=True,
                            ),
                            spacing="3",
                            justify="end",
                            align="end",
                        ),
                        rx.heading("Shared Sections", size="4", margin_top="1rem"),
                        rx.divider(margin_bottom="1rem"),
                        rx.flex(
                            rx.foreach(
                                UserState.all_sections,
                                lambda section: components.form_switch_box(
                                    text=section.title,
                                    name=f"sections_{section.title}",
                                    form_value=section.key.to(str),
                                    selected=False,
                                ),
                            ),
                            wrap="wrap",
                            align="center",
                            justify="center",
                            spacing="4",
                            direction="row",
                        ),
                        direction="column",
                        spacing="4",
                    ),
                    rx.divider(margin_top="1rem"),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="surface",
                                color_scheme="gray",
                                size="4",
                            ),
                        ),
                        rx.form.submit(
                            rx.dialog.close(
                                rx.button(
                                    "Invite",
                                    variant="surface",
                                    size="4",
                                ),
                            ),
                            as_child=True,
                        ),
                        padding_top="2rem",
                        spacing="4",
                        justify="end",
                    ),
                    on_submit=UserState.invite_user,
                    reset_on_submit=False,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            max_width="450px",
            box_shadow="lg",
            padding="1.5rem",
            border="2px solid",
            border_color=rx.color("accent", 7),
            border_radius="25px",
            on_open_auto_focus=[
                UserState.set_all_sections,
                UserState.unset_current_user_sections,
            ],
        ),
    )


def uninvite_user_dialog(user: User) -> rx.Component:
    return rx.dialog.root(
        create_dialog_trigger(
            text="Uninvite",
            icon="user-round-minus",
            color_scheme="crimson",
            button_size="2",
            text_size="3",
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon("user-round-minus", size=34),
                    color_scheme="crimson",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Uninvite User",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Are you sure you want to uninvite this user?",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5rem",
                align_items="center",
                width="100%",
            ),
            rx.divider(),
            rx.heading("User to Uninvite", padding_top="1rem", color_scheme="crimson"),
            rx.hstack(
                rx.text(
                    user.name,
                    padding_bottom="2rem",
                    size="3",
                    font_weight="bold",
                ),
                rx.text(
                    user.email,
                    padding_bottom="2rem",
                    size="3",
                    font_weight="bold",
                ),
                spacing="9",
                margin_top="2rem",
                margin_bottom="1rem",
            ),
            rx.divider(margin_bottom="1.5rem"),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="gray",
                        size="4",
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Uninvite User",
                        variant="surface",
                        color_scheme="crimson",
                        size="4",
                        on_click=UserState.uninvite_user(user),
                    ),
                ),
                spacing="4",
                justify="end",
            ),
            max_width="500px",
            box_shadow="lg",
            padding="1.5rem",
            border="2px solid",
            border_color=rx.color("accent", 7),
            border_radius="25px",
        ),
    )


def update_user_dialog(user: User) -> rx.Component:
    """Create a dialog for updating a user."""
    return rx.dialog.root(
        create_dialog_trigger(text="Edit", icon="square-pen", icon_size=22, button_size="2", text_size="3"),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="square-pen", size=34),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Edit User",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Edit the users's info",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5rem",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        # Username
                        components.not_editable_field(user.username, "user-round", "Plex Username"),
                        # Email
                        components.not_editable_field(user.email, "mail", "Email"),
                        # Full Name
                        components.form_input_field(
                            label="Full Name",
                            placeholder="Full Name",
                            type="text",
                            name="name",
                            icon="user-round",
                            default_value=user.name,
                        ),
                        rx.hstack(
                            # Expiry Date
                            components.form_input_field(
                                label="Expiry Date",
                                placeholder="2025-01-01",
                                type="date",
                                name="expiry_date",
                                icon="calendar-days",
                                default_value=user.expiry_date.to(str),
                            ),
                            # Status
                            components.form_switch_box(
                                text="Never Expire",
                                name="never_expire",
                                form_value=True,
                                selected=user.never_expire,
                                icon="star",
                                display_icon=True,
                            ),
                            spacing="3",
                            justify="end",
                            align="end",
                        ),
                        direction="column",
                        spacing="4",
                    ),
                    rx.divider(margin_top="1rem"),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="surface",
                                color_scheme="gray",
                                size="4",
                            ),
                        ),
                        rx.form.submit(
                            rx.dialog.close(
                                rx.button(
                                    "Update User",
                                    variant="surface",
                                    size="4",
                                ),
                            ),
                            as_child=True,
                        ),
                        padding_top="2rem",
                        spacing="4",
                        justify="end",
                    ),
                    on_submit=UserState.update_user,
                    reset_on_submit=False,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            max_width="450px",
            box_shadow="lg",
            padding="1.5rem",
            border="2px solid",
            border_color=rx.color("accent", 7),
            border_radius="25px",
            on_open_auto_focus=UserState.set_current_user(user),
            on_close_auto_focus=UserState.set_all_users,
        ),
    )


def update_user_sections_dialog(user: User) -> rx.Component:
    return rx.dialog.root(
        create_dialog_trigger(
            text="Share",
            icon="share-2",
            icon_size=22,
            color_scheme="yellow",
            button_size="2",
            text_size="3",
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon("share-2", size=34),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Shared Sections",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Select Sections to share with the user",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5rem",
                align_items="center",
                width="100%",
            ),
            rx.flex(
                rx.form.root(
                    rx.flex(
                        # Name or Username
                        components.not_editable_field(
                            rx.cond(
                                UserState.current_user.name,
                                UserState.current_user.name,
                                UserState.current_user.username,
                            ),
                            "user-round",
                            "User",
                        ),
                        rx.heading("Shared Sections", size="4", margin_top="1rem"),
                        rx.divider(margin_bottom="1rem"),
                        rx.flex(
                            rx.foreach(
                                UserState.all_sections,
                                lambda section: components.form_switch_box(
                                    text=section.title,
                                    name=section.title,
                                    form_value=section.key.to(str),
                                    selected=UserState.current_user_sections[section.key],
                                ),
                            ),
                            wrap="wrap",
                            align="center",
                            justify="center",
                            width="100%",
                            spacing="4",
                            direction="row",
                        ),
                        direction="column",
                        spacing="4",
                    ),
                    rx.divider(margin_top="1rem"),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="surface",
                                color_scheme="gray",
                                size="4",
                            ),
                        ),
                        rx.form.submit(
                            rx.dialog.close(
                                rx.button(
                                    "Update User",
                                    variant="surface",
                                    size="4",
                                ),
                            ),
                            as_child=True,
                        ),
                        padding_top="2rem",
                        spacing="4",
                        justify="end",
                    ),
                    on_submit=UserState.update_user_sections,
                    reset_on_submit=False,
                ),
                width="100%",
                direction="column",
                spacing="4",
            ),
            max_width="450px",
            box_shadow="lg",
            padding="1.5rem",
            border="2px solid",
            border_color=rx.color("accent", 7),
            border_radius="25px",
            on_open_auto_focus=[
                UserState.set_all_sections,
                UserState.set_current_user(user),
                UserState.unset_current_user_sections,
            ],
        ),
    )


def delete_users_dialog(user: User) -> rx.Component:
    return rx.dialog.root(
        create_dialog_trigger(icon="trash-2", icon_size=22, color_scheme="crimson", button_size="2", text_size="3"),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon("trash", size=34),
                    color_scheme="crimson",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Delete User",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "Are you sure you want to delete this users?",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5rem",
                align_items="center",
                width="100%",
            ),
            rx.divider(),
            rx.heading("User to Delete", padding_top="1rem", color_scheme="crimson"),
            rx.hstack(
                rx.text(
                    user.name,
                    padding_bottom="2rem",
                    size="3",
                    font_weight="bold",
                ),
                rx.text(
                    user.email,
                    padding_bottom="2rem",
                    size="3",
                    font_weight="bold",
                ),
                spacing="9",
                margin_top="2rem",
                margin_bottom="1rem",
            ),
            rx.divider(margin_bottom="1.5rem"),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="gray",
                        size="4",
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Delete user",
                        variant="surface",
                        color_scheme="crimson",
                        size="4",
                        on_click=UserState.delete_user(user),
                    ),
                ),
                spacing="4",
                justify="end",
            ),
            max_width="500px",
            box_shadow="lg",
            padding="1.5rem",
            border="2px solid",
            border_color=rx.color("accent", 7),
            border_radius="25px",
        ),
    )


def create_dialog_trigger(
    text: str = "",
    icon: str = "shield-alert",
    icon_size: int = 26,
    text_size: str = "4",
    button_size: str = "3",
    display: bool = True,
    content: str = "",
    color_scheme: str = "iris",
) -> rx.Component:
    if_true = rx.dialog.trigger(
        rx.button(
            rx.icon(icon, size=icon_size),
            rx.cond(
                text != "",
                rx.text(
                    text,
                    size=text_size,
                    display=["none", "none", "block"],
                ),
                rx.fragment(),
            ),
            color_scheme=color_scheme,
            size=button_size,
            variant="surface",
            padding="1rem",
        ),
    )
    if_false = rx.tooltip(
        rx.button(
            rx.icon("refresh-ccw-dot", size=icon_size),
            rx.text("Sync Users", size=text_size, display=["none", "none", "block"]),
            color_scheme=color_scheme,
            size=button_size,
            variant="surface",
            padding="1rem",
            disabled=True,
        ),
        content=content,
    )
    return rx.cond(display, if_true, if_false)


def plex_user_sync_dialog() -> rx.Component:
    return rx.dialog.root(
        create_dialog_trigger(
            text="Sync Users",
            icon="refresh-ccw-dot",
            display=ImportState.enable_sync_users,
            content="You must import sections before syncing users",
        ),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon("refresh-ccw-dot", size=34),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Sync Plex Users",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        """New users will be imported and existing users will be updated.
                        Depending on the number of users and sections this could take a while""",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5rem",
                align_items="center",
                width="100%",
            ),
            rx.divider(),
            rx.heading("Users to Add", padding_top="1rem", color=rx.color("accent", 10)),
            rx.inset(
                rx.skeleton(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Username"),
                                rx.table.column_header_cell("Email"),
                            ),
                        ),
                        rx.table.body(
                            rx.cond(
                                ImportState.new_users.length(),
                                rx.fragment(),
                                rx.table.row(rx.table.cell("No new users"), rx.table.cell("")),
                            ),
                            rx.foreach(
                                ImportState.new_users,
                                lambda user: rx.table.row(
                                    rx.table.cell(user.username),
                                    rx.table.cell(user.email),
                                ),
                            ),
                        ),
                    ),
                    height="4rem",
                    margin="auto",
                    width="90%",
                    loading=rx.cond(ImportState.is_loaded, False, True),
                ),
                side="x",
                margin_top="24px",
                margin_bottom="24px",
            ),
            rx.heading("Users to Update", color=rx.color("accent", 10)),
            rx.inset(
                rx.skeleton(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Username"),
                                rx.table.column_header_cell("Email"),
                            ),
                        ),
                        rx.table.body(
                            rx.cond(
                                ImportState.updated_users.length(),
                                rx.fragment(),
                                rx.table.row(rx.table.cell("No updated users"), rx.table.cell(" ")),
                            ),
                            rx.foreach(
                                ImportState.updated_users,
                                lambda user: rx.table.row(
                                    rx.table.cell(user.username),
                                    rx.table.cell(user.email),
                                ),
                            ),
                        ),
                    ),
                    height="4rem",
                    margin="auto",
                    width="90%",
                    loading=rx.cond(ImportState.is_loaded, False, True),
                ),
                side="x",
                margin_top="24px",
                margin_bottom="24px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="gray",
                        size="4",
                    ),
                ),
                rx.form.submit(
                    rx.dialog.close(
                        rx.button(
                            "Sync Users",
                            variant="surface",
                            size="4",
                            on_click=ImportState.do_user_sync,
                        ),
                    ),
                    as_child=True,
                ),
                spacing="4",
                justify="end",
            ),
            max_width="600px",
            box_shadow="lg",
            padding="1.5rem",
            border="2px solid",
            border_color=rx.color("accent", 7),
            border_radius="25px",
            on_open_auto_focus=[
                ImportState.clear_state,
                ImportState.import_plex_users,
            ],
            on_close_auto_focus=UserState.set_all_users,
        ),
    )


def plex_section_sync_dialog() -> rx.Component:
    return rx.dialog.root(
        create_dialog_trigger(text="Sync Sections", icon="library"),
        rx.dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon("library", size=34),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.dialog.title(
                        "Sync Plex Sections",
                        weight="bold",
                        margin="0",
                    ),
                    rx.dialog.description(
                        "All Sections will be imported",
                    ),
                    spacing="1",
                    height="100%",
                    align_items="start",
                ),
                height="100%",
                spacing="4",
                margin_bottom="1.5rem",
                align_items="center",
                width="100%",
            ),
            rx.divider(),
            rx.heading("Sections to Sync", padding_top="1rem", color=rx.color("accent", 10)),
            rx.inset(
                rx.skeleton(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Section Key"),
                                rx.table.column_header_cell("Section Title"),
                            ),
                        ),
                        rx.table.body(
                            rx.cond(
                                ImportState.update_sections.length(),
                                rx.fragment(),
                                rx.table.row(rx.table.cell("No new sections"), rx.table.cell(" ")),
                            ),
                            rx.foreach(
                                ImportState.update_sections,
                                lambda section: rx.table.row(
                                    rx.table.row_header_cell(section.key),
                                    rx.table.cell(section.title),
                                ),
                            ),
                        ),
                    ),
                    height="4rem",
                    margin="auto",
                    width="90%",
                    loading=rx.cond(ImportState.is_loaded, False, True),
                ),
                side="x",
                margin_top="24px",
                margin_bottom="24px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="surface",
                        color_scheme="gray",
                        size="4",
                    ),
                ),
                rx.form.submit(
                    rx.dialog.close(
                        rx.button(
                            "Sync Sections",
                            variant="surface",
                            size="4",
                            on_click=ImportState.do_section_sync,
                        ),
                    ),
                    as_child=True,
                ),
                spacing="4",
                justify="end",
            ),
            max_width="500px",
            box_shadow="lg",
            padding="1.5rem",
            border="2px solid",
            border_color=rx.color("accent", 7),
            border_radius="25px",
            on_open_auto_focus=[
                ImportState.clear_state,
                ImportState.import_plex_sections,
            ],
        ),
    )
