from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional


class UserBaseSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str
    photo: str | None = None
    role: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    confirm_password: str
    verified: bool = False
    otp: str | None = None


class VerifyUserSchema(BaseModel):
    email: EmailStr
    otp: constr(min_length=6, max_length=6)


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserResponseSchema(UserBaseSchema):
    id: str
    pass


class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema
