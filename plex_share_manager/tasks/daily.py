# Local modules
from ..models import User
from ..utils import plex_connector
from ..utils import utils
from rxconfig import logger, app_settings

# stdlib
import asyncio

# dependencies
import reflex as rx
from sqlmodel import select


async def daily_tasks() -> None:
    logger.info("Starting daily tasks")
    try:
        while True:
            if app_settings["ENABLE_UPDATE_STATUS_TASK"]:
                update_user_status()
            if app_settings["ENABLE_DISABLE_EXPIRED_USERS_TASK"]:
                disable_expired_users()
            await asyncio.sleep(86400)
    except Exception as e:
        logger.error(f"Failed to run daily tasks: {e}")
    logger.info("Daily tasks stopped")


def update_user_status() -> None:
    logger.info("Updating user statuses")
    try:
        with rx.session() as session:
            users = session.exec(select(User)).all()
            for user in users:
                user.expiry_date, user.status = utils.user_status_and_expiry(user.expiry_date, user.never_expire)
                session.add(user)
            session.commit()
    except Exception as e:
        logger.error(f"Failed to update user statuses: {e}")
    logger.info("User statuses updated")


def disable_expired_users() -> None:
    logger.info("Disabling expired users")
    expired_users: list[User] = []
    try:
        with rx.session() as session:
            users = session.exec(select(User)).all()
            for user in users:
                # only pass expired users to the disable_users function
                if user.status == "expired" and user.never_expire is False:
                    expired_users.append(user)
        plex_connector.update_user_access(expired_users)
    except Exception as e:
        logger.error(f"Failed to disable expired users: {e}")
    logger.info("Expired users disabled")
