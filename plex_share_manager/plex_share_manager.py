# Description: Main entry point for the Plex share Manager application.

# Local modules
from .state import UserState
from .ui import base_theme
from .pages import dashboard, settings, SettingState
from .navigation import routes
from .tasks import daily_tasks
from rxconfig import app_settings


# stdlib

# dependencies
import reflex as rx


app = rx.App(
    theme=base_theme(),
    overlay_component=rx.toast.provider(
        rich_colors=True,
        expand=True,
        position="top-center",
        close_button=True,
        duration=10000,
    ),
)

app.add_page(
    settings,
    on_load=SettingState.page_load,
    route=routes.SETTINGS_ROUTE,
)

app.add_page(
    dashboard,
    on_load=UserState.set_all_users,
    route=routes.DASHBOARD_ROUTE,
)

if app_settings["ENABLE_ALL_TASKS"] is True:
    app.register_lifespan_task(daily_tasks)
