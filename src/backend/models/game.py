from beanie import Document, Link
from pydantic import Field
from typing import Optional, List
from src.backend.models.user import User

class Game(Document):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    url: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None

    class Settings:
        name = "games"

class Card(Document):
    game_id: Link[Game]
    card_body: str = Field(default="", max_length=200)
    image_base64: str
    card_title: str = Field(min_length=3, max_length=100)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None

    class Settings:
        name = "cards"

class Score(Document):
    game_id: Link[Game]
    user_id: Link[User]
    username: str
    score: int = Field(ge=0)
    created_at: Optional[str] = None
    
    class Settings:
        name = "scores"