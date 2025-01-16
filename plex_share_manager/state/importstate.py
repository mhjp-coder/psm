# This page is used to import users from Plex into the database.

# Local modules
from ..utils import plex_connector
from ..models import User
from ..models import Section

# stdlib


# dependencies
import reflex as rx
from sqlmodel import select


class ImportState(rx.State):
    update_sections: list[Section] = []
    new_users: list[User] = []
    updated_users: list[User] = []
    # Skeleton loading state
    is_loaded: bool = False
    # Import background state
    running: bool = False

    @rx.event
    def clear_state(self):
        """Clear all state variables"""
        self.set_is_loaded(False)
        self.set_new_users([])
        self.set_updated_users([])
        self.set_update_sections([])

    @rx.var(cache=True)
    def enable_sync_users(self) -> bool:
        """Dont allow sync users if no sections are imported"""
        with rx.session() as session:
            sections = session.exec(select(Section)).all()
            return len(sections) > 0

    @rx.event(background=True)
    async def import_plex_users(self) -> list[User]:
        """Fetch users from Plex server."""
        updated_users: list[User] = []
        new_users: list[User] = []
        async with self:
            self.running = True
        plex_users = plex_connector.get_plex_users()
        if plex_users:
            for user in plex_users:
                if check_user_exists(user.email) is False:
                    new_users.append(user)
                elif user_to_update(user):
                    updated_users.append(user)
        async with self:
            self.new_users = new_users
            self.updated_users = updated_users
            self.running = False
            self.set_is_loaded(True)

    @rx.event(background=True)
    async def do_user_sync(self) -> rx.Component:
        total_users = len(self.new_users) + len(self.updated_users)
        with rx.session() as session:
            if self.new_users != []:
                for user in self.new_users:
                    session.add(user)
            if self.updated_users != []:
                for user in self.updated_users:
                    updated_user = update_user_data(user)
                    session.add(updated_user)
            async with self:
                session.commit()
                self.new_users = []
                self.updated_users = []
        return rx.toast.success(f"Imported and Updated {total_users} Successfully")

    @rx.event(background=True)
    async def import_plex_sections(self):
        """Fetch sections from Plex server."""
        new_sections: list[Section] = []
        async with self:
            self.running = True
        plex_sections = plex_connector.get_plex_sections()
        if plex_sections:
            for section in plex_sections:
                if section_exists(section) is False:
                    new_sections.append(section)
        async with self:
            self.update_sections = new_sections
            self.running = False
            self.set_is_loaded(True)

    @rx.event(background=True)
    async def do_section_sync(self) -> rx.Component:
        total_sections = len(self.update_sections)
        with rx.session() as session:
            for section in self.update_sections:
                session.add(section)
                session.commit()
        async with self:
            self.update_sections = []
        return rx.toast.success(f"Imported and Updated {total_sections} Successfully")


######################
## Helper functions ##
######################


def check_user_exists(email: str) -> bool:
    """Check if a user exists in the database."""
    with rx.session() as session:
        user = session.exec(select(User).where(User.email == email)).one_or_none()
        return user is not None
    return False


def section_exists(section: Section) -> bool:
    with rx.session() as session:
        existing_section = session.exec(select(Section).where(Section.key == section.key)).one_or_none()
        return existing_section is not None


def user_to_update(user: User) -> bool:
    user_should_update: User = User()
    with rx.session() as session:
        user_should_update = session.exec(select(User).where(User.email == user.email)).one_or_none()
        if user_should_update is None:
            return False
        elif (
            user_should_update.username is None
            or user_should_update.email is None
            or user_should_update.plex_id is None
            or user_should_update.avatar_url is None
        ):
            return True
    return False


def update_user_data(user: User) -> User:
    with rx.session() as session:
        existing_user = session.exec(select(User).where(User.email == user.email)).one()
    setattr(existing_user, "username", user.username)
    setattr(existing_user, "email", user.email)
    setattr(existing_user, "plex_id", user.plex_id)
    setattr(existing_user, "avatar_url", user.avatar_url)
    return existing_user
