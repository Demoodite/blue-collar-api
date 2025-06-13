from os import stat

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import state
from sqlmodel import Session, SQLModel, select

from api import requests, responses
from auth import auth
from db.engine import engine as db_engine
from db.models import Employee, Entrance, User

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(db_engine)


@app.post("/user/register", response_model=responses.Message, status_code=201)
def register(register_request: requests.Register):
    if auth.get_user_by_username(register_request.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = auth.get_password_hash(register_request.password)
    user = User(username=register_request.username, password_hash=hashed_password)
    with Session(db_engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return responses.Message(message=f"User {user.username} created")


@app.post("/user/login", response_model=responses.Login, status_code=202)
def login(login_request: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = auth.create_access_token(data={"sub": user.username})
    return responses.Login(access_token=access_token, token_type="Bearer")


@app.get("/employee", response_model=responses.Employee)
def get_employee_info(user: User = Depends(auth.get_current_user)):
    with Session(db_engine) as session:
        statement = select(Employee).where(Employee.user_id == user.id)
        employee = session.exec(statement).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.post("/employee", response_model=responses.Employee, status_code=201)
def post_employee_info(
    employee_request: requests.Employee, user: User = Depends(auth.get_current_user)
):
    with Session(db_engine) as session:
        statement = select(Employee).where(Employee.user_id == user.id)
        if not session.exec(statement).first() is None:
            raise HTTPException(status_code=400, detail="Employee already exists")
        employee = Employee(
            user_id=user.id,
            name=employee_request.name,
            title=employee_request.title,
            current_task=employee_request.current_task,
        )
        session.add(employee)
        session.commit()
        session.refresh(employee)
    return employee


@app.put("/employee", response_model=responses.Employee)
def put_employee_info(
    employee_request: requests.Employee, user: User = Depends(auth.get_current_user)
):
    with Session(db_engine) as session:
        statement = select(Employee).where(Employee.user_id == user.id)
        employee = session.exec(statement).first()
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        employee.name = employee_request.name
        employee.title = employee_request.title
        employee.current_task = employee_request.current_task
        session.add(employee)
        session.commit()
        session.refresh(employee)
    return employee
