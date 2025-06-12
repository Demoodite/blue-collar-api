from uuid import uuid4

from fastapi import FastAPI, HTTPException
from sqlmodel import Session, SQLModel, select

from api.requests import *
from api.responses import *
from db.engine import engine
from db.models import Employee, Entrance, Token, User

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/register", response_model=MessageResponse)
def register(register_request: RegisterRequest):
    with Session(engine) as session:
        if session.exec(
            select(User).where(User.username == register_request.username)
        ).first():
            raise HTTPException(status_code=400, detail="User already exists")
        user = User(
            username=register_request.username, password=register_request.password
        )
        session.add(user)
        session.commit()
        return MessageResponse(message=f"User {user.username} registered")


@app.post("/login", response_model=LoginResponse)
def login(login_request: LoginRequest):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == login_request.username)
        ).first()
        if not user or user.password != login_request.password:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token = str(uuid4())
        if user.id == None:
            raise HTTPException(status_code=400, detail="Invalid user")
        session.add(Token(token=token, user_id=user.id))
        session.commit()
        return LoginResponse(access_token=token, token_type="Bearer")
