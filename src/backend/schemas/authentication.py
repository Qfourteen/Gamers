from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    username: str
    disabled: bool = False
    is_admin: bool = False
    disabled_reason: Optional[str] = None
    disabled_at: Optional[datetime] = None


class UserCreate(BaseModel):
    username: str
    password: str


class AccountAction(BaseModel):
    """계정 활성화/비활성화를 위한 요청 모델"""
    reason: Optional[str] = None


class AdminUserAction(BaseModel):
    """관리자의 사용자 관리 작업을 위한 요청 모델"""
    username: str
    reason: Optional[str] = None