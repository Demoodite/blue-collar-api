from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
