# 데이터 구조

## 3줄 요약
1. 이 프로젝트에서는 [mongodb](https://namu.wiki/w/MongoDB) 데이터베이스를 사용합니다.
2. mongodb를 파이썬에서 쉽게 이용할 수 있도록 [beanie](https://beanie-odm.dev/) 라이브러리를 사용합니다.
3. mongodb는 데이터 필드 조정이 유동적이나, 
beanie가 실행 중 안정성을 보장하기 위해 파이썬 클래스로 데이터 필드를 강제합니다. (확장 쉽고 안정성 높음)

## 데이터베이스 레벨(Mongodb↔Backend)
### Game
```python
from beanie import Document
from pydantic import Field
from typing import List

class Game(Document):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    url: str
```

### Card
```python
from beanie import Document, Link
from pydantic import Field

class Card(Document):
    game_id: Link[Game]
    card_body: str = Field(default="", max_length=200)
    image_url: str
    card_title: str = Field(min_length=3, max_length=100)
```

## 애플리케이션 레벨(Backend↔Frontend)
### SearchResult
```python
from pydantic import BaseModel, Field
from typing import List

class SearchResult(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    tags: List[str] = Field(default_factory=list)
    game_id: str
```

### CardResult
```python
from pydantic import BaseModel, Field

class CardResult(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    image_url: str
    card_title: str = Field(min_length=3, max_length=100)
    game_id: str
```