from datetime import datetime
from math import floor

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, SQLModel, null, select

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
        if session.exec(statement).first() is not None:
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


@app.post("/employee/enter", response_model=responses.Entrance)
def employee_enter(user: User = Depends(auth.get_current_user)):
    with Session(db_engine) as session:
        statement = (
            select(Entrance)
            .where(Entrance.user_id == user.id)
            .where(Entrance.leave_timestamp == null())
        )

        if session.exec(statement).first() is not None:
            raise HTTPException(status_code=403, detail="Already entered")
        assert user.id is not None
        enterance = Entrance(user_id=user.id, enter_timestamp=datetime.now())
        session.add(enterance)
        session.commit()
        session.refresh(enterance)
    return responses.Entrance(
        enter_timestamp=floor(enterance.enter_timestamp.timestamp()),
        leave_timestamp=None,
    )


@app.post("/employee/leave", response_model=responses.Entrance)
def employee_leave(user: User = Depends(auth.get_current_user)):
    with Session(db_engine) as session:
        statement = (
            select(Entrance)
            .where(Entrance.user_id == user.id)
            .where(Entrance.leave_timestamp == null())
        )
        enterance = session.exec(statement).first()
        if enterance is None:
            raise HTTPException(status_code=403, detail="Hasn't entered")
        assert user.id is not None
        enterance.leave_timestamp = datetime.now()
        session.add(enterance)
        session.commit()
        session.refresh(enterance)
    return responses.Entrance(
        enter_timestamp=floor(enterance.enter_timestamp.timestamp()),
        leave_timestamp=floor(enterance.leave_timestamp.timestamp()),
    )
