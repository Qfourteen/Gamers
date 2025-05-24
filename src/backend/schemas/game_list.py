from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SearchResult(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    tags: List[str] = Field(default_factory=list)
    game_id: str

class CardResult(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    image_base64: str
    card_title: str = Field(min_length=3, max_length=100)
    game_id: str

class GameCreate(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    url: str

class GameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=30)
    short_description: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    url: Optional[str] = None

class GameResponse(BaseModel):
    id: str
    name: str
    short_description: str
    description: str
    tags: List[str]
    url: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None

class CardCreate(BaseModel):
    game_id: str
    card_body: str = Field(default="", max_length=200)
    image_base64: str
    card_title: str = Field(min_length=3, max_length=100)

class CardUpdate(BaseModel):
    card_body: Optional[str] = Field(None, max_length=200)
    image_base64: Optional[str] = None
    card_title: Optional[str] = Field(None, min_length=3, max_length=100)

class CardResponse(BaseModel):
    id: str
    game_id: str
    card_body: str
    image_base64: str
    card_title: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None

class ScoreCreate(BaseModel):
    game_url: str
    score: int = Field(ge=0)

class ScoreResponse(BaseModel):
    id: str
    game_id: str
    username: str
    score: int
    created_at: Optional[str] = None

