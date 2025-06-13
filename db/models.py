from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password_hash: str


class Employee(SQLModel, table=True):
    user_id: int | None = Field(foreign_key="user.id", primary_key=True)
    name: str
    title: str
    current_task: str


class Entrance(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    enter_timestamp: datetime
    leave_timestamp: datetime | None = Field(default=None)
