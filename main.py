from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, SQLModel

from api.requests import *
from api.responses import *
from auth.auth import *
from db.engine import *
from db.models import *

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/register", response_model=MessageResponse)
def register(register_request: RegisterRequest):
    if get_user_by_username(register_request.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(register_request.password)
    user = User(username=register_request.username, password_hash=hashed_password)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return MessageResponse(message=f"User {user.username} created")


@app.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return LoginResponse(access_token=access_token, token_type="Bearer")
