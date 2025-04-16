from pydantic import BaseModel, Field
from typing import Optional, List

class SearchResult(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    tags: List[str] = Field(default_factory=list)
    game_id: str

class CardResult(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    image_url: str
    card_title: str = Field(min_length=3, max_length=100)
    game_id: str

