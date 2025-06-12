from sqlmodel import Field, SQLModel, create_engine


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str


class Token(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token: str
    user_id: int = Field(foreign_key="user.id")


class Employee(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    name: str
    title: str
    current_task: str


class Entrance(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    enterTimestamp: int
    leaveTimestamp: int


engine = create_engine("sqlite:///bcollar.db")
