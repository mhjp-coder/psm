# This file contains utility functions that are used in the application

# Local modules
from rxconfig import app_settings

# stdlib
from datetime import date, timedelta


# dependencies


def user_status_and_expiry(expiry_date: date | str, never_expire: bool) -> tuple[date, str]:
    """Calculate the status of a user based on their expiry date."""
    status: str = "expired"
    if expiry_date is None or expiry_date == "":
        expiry_date = date.today() + timedelta(days=app_settings["DEFAULT_EXPIRY_DAYS"])
    elif isinstance(expiry_date, str):
        expiry_date = date.fromisoformat(expiry_date)
    delta = (expiry_date - date.today()).days
    if never_expire is True:
        status = "never"
    else:
        status = "expired" if delta < 0 else "expiring" if delta <= 30 else "active"
    return expiry_date, status
