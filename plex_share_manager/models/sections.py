# This file contains the Section model

# Local modules

# stdlib

# dependencies
from sqlmodel import Relationship, Field
import reflex as rx


# association table
class UserSectionLink(rx.Model, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    section_id: int | None = Field(default=None, foreign_key="section.id", primary_key=True)


class Section(rx.Model, table=True):
    key: int
    title: str
    users: list["User"] = Relationship(back_populates="sections", link_model=UserSectionLink)
