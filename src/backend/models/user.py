from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from ..utility import utc_now_factory

class User(Document):
    username: str = Field(min_length=3, max_length=100)
    hashed_password: str
    disabled: bool = False
    created_at: datetime = Field(default_factory=utc_now_factory)
    last_login: Optional[datetime] = None
    
    class Settings:
        name = "users"
