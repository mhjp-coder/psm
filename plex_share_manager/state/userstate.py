# Main dashboard page for the application.

# Local modules
from ..models import User, Section
from ..utils import utils, plex_connector
from .importstate import check_user_exists

# stdlib

# dependencies
import reflex as rx
from sqlalchemy.orm import selectinload
from sqlmodel import select, asc, desc, or_


class UserState(rx.State):
    # User State vars
    all_users: rx.Field[list[User]] = rx.field(list[User]())
    current_user: rx.Field[User] = rx.field(User())
    all_sections: rx.Field[list[Section]] = rx.field(list[Section]())
    current_user_sections: rx.Field[dict[int, bool]] = rx.field(dict())
    form_data: rx.Field[dict] = rx.field(dict())
    # Sort and Filter vars
    _FIELD_MAPPING = {
        "ID": "plex_id",
        "Name": "name",
        "Username": "username",
        "Email": "email",
        "Expiry Date": "expiry_date",
    }
    sort_options: list[str] = [key for key in _FIELD_MAPPING.keys()]
    sort_reverse: bool = False
    sort_value: str = ""
    filter_value: str = ""

    @rx.event
    def set_all_users(self) -> None:
        """Set State.var "users" from User DB Model, Filter(search) and Sort"""
        with rx.session() as session:
            query = select(User)
            # Filter based on search input value
            if self.filter_value != "":
                filter_value = f"%{self.filter_value.lower()}%"
                query = query.where(
                    or_(
                        User.id.ilike(filter_value),
                        User.name.ilike(filter_value),
                        User.username.ilike(filter_value),
                        User.email.ilike(filter_value),
                        User.expiry_date.ilike(filter_value),
                    )
                )
            # Sort based on the selected column
            if self.sort_value != "":
                sort_column = getattr(User, self.sort_value)
                order = desc(sort_column) if self.sort_reverse else asc(sort_column)
                query = query.order_by(order)
            # Set all | filtered users
            self.all_users = session.exec(query).all()

    @rx.event
    def set_current_user(self, user: User) -> None:
        """Set State.var "user" from User DB Model"""
        with rx.session() as session:
            statement = select(User).options(selectinload(User.sections)).where(User.id == user.id)
            self.current_user = session.exec(statement).unique().first()
            self.current_user_sections = {section.key: True for section in self.current_user.sections}

    @rx.event
    def unset_current_user_sections(self) -> None:
        """Get the current user's sections"""
        self.current_user_sections = {}

    @rx.event
    def set_filter_values(self, search_input_value: str) -> None:
        """Filter users based on the search value"""
        self.filter_value = search_input_value
        self.set_all_users()

    @rx.event
    def set_toggle_sort(self) -> None:
        """Toggle the sort order"""
        self.sort_reverse = not self.sort_reverse
        self.set_all_users()

    @rx.event
    def set_sort_values(self, display_name: str) -> None:
        """Convert display name to database field name"""
        self.sort_value = self._FIELD_MAPPING.get(display_name, "")
        self.set_all_users()

    @rx.event
    def set_all_sections(self) -> None:
        """Set State.var "all_sections" from Section DB Model"""
        with rx.session() as session:
            self.all_sections = session.exec(select(Section)).all()

    @rx.event
    def update_user(self, form_data: dict) -> rx.Component:
        """Update the name of a user."""
        self.form_data = form_data
        # Check and set the expiry date and status
        expiry_date, status = utils.user_status_and_expiry(
            self.form_data["expiry_date"],
            self.form_data["never_expire"],
        )
        # Update the user in the database
        with rx.session() as session:
            try:
                user = session.exec(select(User).where(User.id == self.current_user.id)).one_or_none()
                if not user:
                    return rx.toast.error("User not found")
                setattr(user, "expiry_date", expiry_date)
                setattr(user, "status", status)
                setattr(user, "name", self.form_data["name"])
                setattr(user, "never_expire", self.form_data["never_expire"])
                session.add(user)
                session.commit()
                if user.plex_id is not None:
                    # Update the user in Plex, Must be list
                    plex_connector.update_user_access([user])
                self.set_all_users()
                return rx.toast.success("User successfully updated")
            except Exception as e:
                session.rollback()
                return rx.toast.error(f"Error updating user: {e}")

    @rx.event
    def update_user_sections(self, form_data: dict) -> rx.Component:
        """Update the sections of a user."""
        self.form_data = form_data
        # selected sections
        section_keys: list[int] = [int(value) for value in self.form_data.values()]
        # Update the user in the database
        with rx.session() as session:
            try:
                user = session.exec(select(User).where(User.id == self.current_user.id)).one_or_none()
                if not user:
                    return rx.toast.error("User not found")
                sections = session.exec(select(Section).filter(Section.key.in_(section_keys))).all()
                user.sections = sections
                session.add(user)
                session.commit()
                if user.plex_id is not None:
                    # Update the user in Plex, Must be list
                    plex_connector.update_user_access([user])
                self.set_all_users()
                return rx.toast.success(
                    f"Successfully set users sections to: {[name for name in self.form_data.keys()]}"
                )
            except Exception as e:
                session.rollback()
                return rx.toast.error(f"Error updating user sections: {e}")

    @rx.event
    def delete_user(self, user: User) -> rx.Component:
        """Delete a user from the database."""
        with rx.session() as session:
            try:
                user_to_delete = session.exec(select(User).where(User.id == user.id)).one_or_none()
                if user_to_delete.plex_id is not None:
                    # Disable the user in Plex
                    plex_connector.update_user_access([user], delete=True)
                session.delete(user_to_delete)
                session.commit()
                self.set_all_users()
                return rx.toast.success(f"User {user.email} successfully deleted")
            except Exception as e:
                session.rollback()
                return rx.toast.error(f"User not found or error deleting user: {e}")

    @rx.event
    def invite_user(self, form_data: dict) -> rx.Component:
        """Invite a user to the Plex server."""
        # Split form data into two sections
        self.current_user_sections = dict({k: v for k, v in form_data.items() if k.startswith("sections_")})
        user = {k: v for k, v in form_data.items() if k.startswith("user_")}
        clean_user = {key.replace("user_", ""): value for key, value in user.items()}
        self.current_user = User(**clean_user)

        section_keys = list(self.current_user_sections.values())
        # Check and set user attributes
        self.current_user.expiry_date, self.current_user.status = utils.user_status_and_expiry(
            self.current_user.expiry_date,
            self.current_user.never_expire,
        )
        self.current_user.invite_pending = True
        if not self.current_user.email:
            return rx.toast.error("Email Required")
        elif check_user_exists(self.current_user.email):
            return rx.toast.error("User with this email already exists")
        # Set sections
        with rx.session() as session:
            sections = session.exec(select(Section).where(Section.key.in_(section_keys))).all()
            self.current_user.sections = sections
            try:
                # Send to plex server
                plex_connector.invite_new_user(self.current_user, sections)
                # add the user to the database
                session.add(self.current_user)
                session.commit()
                session.refresh(self.current_user)

                self.set_all_users()
                return rx.toast.success(f"User {self.current_user.email} successfully invited")
            except Exception as e:
                session.rollback()
                return rx.toast.error(f"Error inviting user: {e}")

    @rx.event
    def uninvite_user(self, user: User) -> rx.Component:
        """Uninvite a user from the Plex server."""
        with rx.session() as session:
            try:
                user_to_delete = session.exec(select(User).where(User.id == user.id)).one_or_none()
                if user_to_delete.plex_id is not None:
                    # Disable the user in Plex
                    plex_connector.uninvite_user(user)
                session.delete(user_to_delete)
                session.commit()
                self.set_all_users()
                return rx.toast.success(f"User {user.email} successfully uninvited")
            except Exception as e:
                session.rollback()
                return rx.toast.error(f"User not found or error uninviting user: {e}")


######################
## Helper functions ##
######################
