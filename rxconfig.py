# Config file for reflex

# local modules

# stdlib
import os
import logging
from pathlib import Path
import tomllib as toml
import shutil

# dependencies
import reflex as rx

# Setup config file
config_file = Path(__file__).parent / "data/config.toml"

if not config_file.exists():
    default_config_file = Path(__file__).parent / "plex_share_manager/default_config.toml"
    shutil.copy2(default_config_file, config_file)


class ConfigState:
    config_file: Path = Path(__file__).parent / "data/config.toml"
    app_settings: dict = {}

    def load_settings_toml(self) -> None:
        """Load the settings from the environment variables."""
        with open(self.config_file, "rb") as f:
            settings = toml.load(f)

        if os.getenv("PLEXAPI_AUTH_SERVER_TOKEN"):
            settings["PLEXAPI_AUTH_SERVER_TOKEN"] = os.getenv("PLEXAPI_AUTH_SERVER_TOKEN")

        if os.getenv("PLEXAPI_AUTH_SERVER_BASEURL"):
            settings["PLEXAPI_AUTH_SERVER_BASEURL"] = os.getenv("PLEXAPI_AUTH_SERVER_BASEURL")

        self.app_settings = settings


# Create and use the state instance
config_state = ConfigState()
config_state.load_settings_toml()

config = rx.Config(
    app_name="plex_share_manager",
    db_url="sqlite:///data/reflex.db",
    api_url="http://localhost:8000",
    state_manager_mode="redis",
    redis_url="redis://localhost",
)


logging.basicConfig(
    level=getattr(logging, config_state.app_settings["LOG_LEVEL"]),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("psm_logger")
