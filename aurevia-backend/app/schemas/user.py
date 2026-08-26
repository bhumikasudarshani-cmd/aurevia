from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=80)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str | None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this from an ORM object directly


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
