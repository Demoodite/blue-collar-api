from fastapi import FastAPI, HTTPException
from sqlmodel import Session, SQLModel, select

from db.engine import engine
from db.models import Employee, Entrance, Token, User

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/register")
def register(username: str, password: str):
    with Session(engine) as session:
        if session.exec(select(User).where(User.username == username)).first():
            raise HTTPException(status_code=400, detail="User already exists")
        user = User(username=username, password=password)
        session.add(user)
        session.commit()
        return {"message": "User registered"}
