# This file contains the User model which is used to represent a user in the database.

# Local modules
from .sections import Section, UserSectionLink

# stdlib
from datetime import date

# dependencies
import reflex as rx
from sqlmodel import Field, Relationship
import sqlalchemy


class User(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plex_id: int = Field(default=None)
    name: str = Field(default=None)
    username: str = Field(default=None)
    email: str = Field(unique=True)
    avatar_url: str = Field(default=None)
    never_expire: bool = Field(default=False)
    invite_pending: bool = Field(default=False)
    expiry_date: date = Field(
        default=None,
        sa_column=sqlalchemy.Column(
            "expiry_date",
            sqlalchemy.Date,
        ),
    )
    status: str = Field(default="expired")
    sections: list[Section] = Relationship(back_populates="users", link_model=UserSectionLink)
