# This file contains the home page for the application

# Local modules
from ..ui import base_page
from ..models import Section
from rxconfig import logger, config_state, config_file

# stdlib

# dependencies
import reflex as rx
import tomllib as toml
from sqlmodel import select
import tomli_w as toml_w


class SettingState(rx.State):
    _config: toml
    _log_levels: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    _expiry_days_list: list[str] = ["0", "1", "2", "3", "4", "5", "10", "20", "30", "60", "90", "120"]
    plextoken: str
    plexbaseurl: str
    section_choices: dict[str, bool] = {}
    default_expiry_days: str
    enable_all_tasks: bool
    enable_update_status_task: bool
    enable_disable_expired_users_task: bool
    allow_sync: bool
    log_level: str

    @rx.event
    def page_load(self) -> None:
        """Load config file and set choices."""
        # Load config file
        with open(config_file, "rb") as f:
            self._config = toml.load(f)
        # Get all sections from the database
        with rx.session() as session:
            choices = session.exec(select(Section)).all()
        # Create a dictionary of choices
        choices_values = {section.title: False for section in choices}
        # Set the state values
        selected = self._config["SECTION_EXPIRED"]
        choices_values[selected] = True
        self.section_choices = choices_values
        self.default_expiry_days = str(self._config["DEFAULT_EXPIRY_DAYS"])
        self.enable_all_tasks = self._config["ENABLE_ALL_TASKS"]
        self.enable_update_status_task = self._config["ENABLE_UPDATE_STATUS_TASK"]
        self.enable_disable_expired_users_task = self._config["ENABLE_DISABLE_EXPIRED_USERS_TASK"]
        self.log_level = self._config["LOG_LEVEL"]
        self.allow_sync = self._config["ALLOW_SYNC"]
        self.plextoken = self._config["PLEXAPI_AUTH_SERVER_TOKEN"]
        self.plexbaseurl = self._config["PLEXAPI_AUTH_SERVER_BASEURL"]

    @rx.event
    def change_plextoken(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.plextoken = value
        self._config["PLEXAPI_AUTH_SERVER_TOKEN"] = value
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()

    @rx.event
    def change_plexbaseurl(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.plexbaseurl = value
        self._config["PLEXAPI_AUTH_SERVER_BASEURL"] = value
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()

    @rx.event
    def check_choice(self, value, index) -> None:
        """Update config values and write to config file."""
        # Set all other checkboxes to False
        for key in self.section_choices:
            if key != index:
                self.section_choices[key] = False
        # Set the current checkbox to the value
        self.section_choices[index] = value
        # Update the config file
        self._config["SECTION_EXPIRED"] = index
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()

    @rx.event
    def change_expiry_days(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.default_expiry_days = value
        self._config["DEFAULT_EXPIRY_DAYS"] = int(value)
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()

    @rx.event
    def change_enable_all_tasks(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.enable_all_tasks = value
        self._config["ENABLE_ALL_TASKS"] = value
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()

    @rx.event
    def change_enable_update_status_task(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.enable_update_status_task = value
        self._config["ENABLE_UPDATE_STATUS_TASK"] = value
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()

    @rx.event
    def change_enable_disable_expired_users_task(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.enable_disable_expired_users_task = value
        self._config["ENABLE_DISABLE_EXPIRED_USERS_TASK"] = value
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()

    @rx.event
    def change_log_level(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.log_level = value
        self._config["LOG_LEVEL"] = value
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        logger.setLevel(value)
        config_state.load_settings_toml()

    @rx.event
    def change_allow_sync(self, value) -> None:
        """Update config values and write to config file."""
        # Update the config file
        self.allow_sync = value
        self._config["ALLOW_SYNC"] = value
        with open(config_file, "wb") as f:
            toml_w.dump(self._config, f)
        config_state.load_settings_toml()


def settings() -> rx.Component:
    return base_page(
        rx.box(
            rx.badge(
                rx.icon("settings", size=28),
                rx.heading("Settings", size="6"),
                radius="full",
                align="center",
                variant="outline",
                padding="1rem",
            ),
            rx.divider(margin_y="2rem"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Plex Server Token", _as="h1"),
                        rx.text("This is the token used to authenticate with the PlexAPI Auth Server."),
                        rx.text(
                            rx.link(
                                "Instructions",
                                href="https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
                            )
                        ),
                        rx.text(rx.text.strong(".env entry will override this value")),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    render_input(
                        SettingState.plextoken,
                        SettingState.change_plextoken,
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Plex Server BaseURL", _as="h1"),
                        rx.text("This is the URL of the Plex Server. i.e. http://plex.yourdomain.com:32400"),
                        rx.text(rx.text.strong(".env entry will override this value")),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    render_input(
                        SettingState.plexbaseurl,
                        SettingState.change_plexbaseurl,
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Expired Section", _as="h1"),
                        rx.text("This is the section to assign expired users."),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    render_checkboxes(
                        SettingState.section_choices,
                        SettingState.check_choice,
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Default Expiry Days", _as="h1"),
                        rx.text(
                            "When importing new users, this value is added the the current date to set the expiry date."
                        ),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    render_select(
                        SettingState.default_expiry_days,
                        SettingState._expiry_days_list,
                        SettingState.change_expiry_days,
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("All Tasks", _as="h1"),
                        rx.text("Turn on to enable all tasks to run daily. Turn off to disable all tasks."),
                        rx.text(rx.text.strong("Restart required")),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        render_switch(
                            SettingState.enable_all_tasks,
                            SettingState.change_enable_all_tasks,
                        ),
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Update Status Task", _as="h1"),
                        rx.text(
                            "Turn on to enable the update status task to run daily. This task updates the status of the users in the database based on the expiry date."
                        ),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        render_switch(
                            SettingState.enable_update_status_task,
                            SettingState.change_enable_update_status_task,
                        ),
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Disable Expired Users Task", _as="h1"),
                        rx.text(
                            """Turn on to enable the update status task to run daily.
                            This task updates the status of the users in the database based on the expiry date."""
                        ),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        render_switch(
                            SettingState.enable_disable_expired_users_task,
                            SettingState.change_enable_disable_expired_users_task,
                        ),
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Allow Sync", _as="h1"),
                        rx.text("Allow plex users to download content from the server."),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        render_switch(
                            SettingState.allow_sync,
                            SettingState.change_allow_sync,
                        ),
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Log Level", _as="h1"),
                        rx.text("Set the Application log level."),
                        rx.text(rx.text.strong("Restart required")),
                        max_width="30%",
                    ),
                    rx.spacer(),
                    render_select(
                        SettingState.log_level,
                        SettingState._log_levels,
                        SettingState.change_log_level,
                    ),
                    width="50%",
                ),
                rx.divider(margin_y="2rem", width="60%"),
                align="center",
            ),
        ),
    )


def render_input(value, handler) -> rx.Component:
    return rx.input(
        value=value,
        on_change=handler,
        size="3",
        variant="soft",
        width="20rem",
    )


def render_checkboxes(values, handler) -> rx.Component:
    return rx.vstack(
        rx.foreach(
            values,
            lambda choice: rx.checkbox(
                choice[0],
                checked=choice[1],
                on_change=lambda val: handler(val, choice[0]),
                variant="soft",
                spacing="2",
                size="3",
            ),
        ),
        wrap="wrap",
        spacing="3",
    )


def render_select(value, items, handler) -> rx.Component:
    return rx.select(
        items=items,
        value=value,
        on_change=lambda val: handler(val),
        size="3",
        variant="soft",
        width="8rem",
    )


def render_switch(value, handler) -> rx.Component:
    return rx.switch(
        name="enable_all_tasks",
        checked=value,
        value="True",
        size="3",
        radius="full",
        variant="soft",
        on_change=handler,
    )
