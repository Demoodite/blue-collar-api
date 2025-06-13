from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Login(BaseModel):
    access_token: str
    token_type: str


class Employee(BaseModel):
    name: str
    title: str
    current_task: str


class Entrance(BaseModel):
    enter_timestamp: int
    leave_timestamp: int | None
