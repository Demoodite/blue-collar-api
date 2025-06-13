from pydantic import BaseModel


class Register(BaseModel):
    username: str
    password: str


class Login(BaseModel):
    username: str
    password: str


class Employee(BaseModel):
    name: str
    title: str
    current_task: str
