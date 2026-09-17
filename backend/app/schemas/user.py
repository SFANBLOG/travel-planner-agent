"""用户相关 Pydantic 模型"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    # 支持用户名或邮箱登录
    identifier: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class UserUpdate(BaseModel):
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    avatar_url: Optional[str] = None
    preferences: dict = {}
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
