from beanie import Document, Link
from pydantic import Field
from typing import Optional, List

class Game(Document):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    url: str

class Card(Document):
    game_id: Link[Game]
    card_body: str = Field(default="", max_length=200)
    image_url: str
    card_title: str = Field(min_length=3, max_length=100)