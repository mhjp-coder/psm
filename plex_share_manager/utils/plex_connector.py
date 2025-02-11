# Plex Connector and User Management utilities

# Local modules
from ..models import User, Section
from ..utils import utils
from rxconfig import config_state, logger

# stdlib

# dependencies
import reflex as rx
from sqlmodel import select
from plexapi.myplex import PlexServer

# Constants
allow_sync = 1 if config_state.app_settings["ALLOW_SYNC"] else 0
_plex_server = None  # Cache connection


def _connect_plex_server() -> PlexServer:
    """Connect to Plex server with caching."""
    global _plex_server
    try:
        if _plex_server is None:
            _plex_server = PlexServer(
                baseurl=config_state.app_settings["PLEXAPI_AUTH_SERVER_BASEURL"],
                token=config_state.app_settings["PLEXAPI_AUTH_SERVER_TOKEN"],
            )
    except Exception as e:
        logger.error(f"Failed to connect to Plex server: {e}")
    return _plex_server


def get_plex_users() -> list[User]:
    """Fetch users from Plex server."""
    users: list[User] = []
    local_sections: list = []
    with rx.session() as session:
        local_sections = session.exec(select(Section)).all()
    try:
        plex_server = _connect_plex_server()
        plex_users = plex_server.myPlexAccount().users()
        pending_invites = plex_server.myPlexAccount().pendingInvites(includeReceived=False)

    except Exception as e:
        logger.error(f"Failed to fetch Plex users: {e}")
        raise e
    try:
        expiry_date, status = utils.user_status_and_expiry(None, None)

        for plex_user in plex_users:
            if plex_user.email is None:
                continue
            new_user_sections = get_users_sections(plex_user.email)
            # Filter sections that user has access to
            new_user = User(
                plex_id=plex_user.id,
                username=plex_user.title,
                email=plex_user.email,
                expiry_date=expiry_date,
                status=status,
                avatar_url=plex_user.thumb,
                sections=[section for section in local_sections if section.key in new_user_sections],
                invite_pending=False,
            )
            users.append(new_user)

        for plex_user in pending_invites:
            pending_user = User(
                plex_id=None,
                username=None,
                email=plex_user.email,
                expiry_date=expiry_date,
                status=status,
                avatar_url=None,
                sections=[],
                invite_pending=True,
            )
            users.append(pending_user)

    except Exception as e:
        logger.error(f"Error processing user {plex_user.email}: {e}")
    return users


def get_users_sections(user_email: str) -> list[str]:
    """Fetch library sections shared with Plex user."""
    try:
        user_sections: list[str] = []
        plex_server = _connect_plex_server()
        all_sections = plex_server.myPlexAccount().user(user_email).server(plex_server.friendlyName).sections()
        for section in all_sections:
            if section.shared:
                user_sections.append(section.key)
    except Exception as e:
        logger.error(f"Failed to fetch user sections for {user_email}: {e}")
    return user_sections


def get_plex_sections() -> list[Section]:
    """Fetch library sections from Plex server."""
    try:
        sections: list[Section] = []
        plex_server = _connect_plex_server()
        server_sections = plex_server.library.sections()
        for section in server_sections:
            sections.append(Section(key=section.key, title=section.title))
    except Exception as e:
        logger.error(f"Failed to fetch Plex sections: {e}")
    return sections


def update_user_access(users: list[User], delete=False) -> None:
    """Update user access to Plex library sections."""
    try:
        plex_server = _connect_plex_server()
        account = plex_server.myPlexAccount()
        for user in users:
            sections = [section.title for section in user.sections]
            user_email = account.user(user.email)
            if user.status == "expired" or delete is True:
                account.updateFriend(user_email, plex_server, sections=[config_state.app_settings["SECTION_EXPIRED"]])
            else:
                account.updateFriend(user_email, plex_server, sections=sections, allowSync=allow_sync)
    except Exception as e:
        logger.error(f"Failed to update user {user.email}: {e}")
    return None


def invite_new_user(user: User, sections: Section) -> None:
    """Invite a new user to the Plex server."""
    sections = [section.title for section in sections]
    try:
        plex_server = _connect_plex_server()
        account = plex_server.myPlexAccount()
        account.inviteFriend(user.email, plex_server, sections=sections, allowSync=allow_sync)
    except Exception as e:
        logger.error(f"Failed to invite user {user.email}: {e}")
    return None


def uninvite_user(user: User) -> None:
    """Uninvite a user from the Plex server."""
    try:
        plex_server = _connect_plex_server()
        account = plex_server.myPlexAccount()
        account.cancelInvite(user.email)
    except Exception as e:
        logger.error(f"Failed to uninvite user {user.email}: {e}")
    return None
