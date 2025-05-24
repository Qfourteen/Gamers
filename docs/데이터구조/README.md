# 데이터 구조

## 3줄 요약
1. 이 프로젝트에서는 [mongodb](https://namu.wiki/w/MongoDB) 데이터베이스를 사용합니다.
2. mongodb를 파이썬에서 쉽게 이용할 수 있도록 [beanie](https://beanie-odm.dev/) 라이브러리를 사용합니다.
3. mongodb는 데이터 필드 조정이 유동적이나, 
beanie가 실행 중 안정성을 보장하기 위해 파이썬 클래스로 데이터 필드를 강제합니다. (확장 쉽고 안정성 높음)

## 데이터베이스 레벨(Mongodb↔Backend)

> `models`라고도 불립니다.

### User
```python
from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class User(Document):
    username: str = Field(min_length=3, max_length=100)
    hashed_password: str
    disabled: bool = False
    is_admin: bool = False
    created_at: datetime = Field(default_factory=utc_now_factory)
    last_login: Optional[datetime] = None
    disabled_reason: Optional[str] = None
    disabled_at: Optional[datetime] = None
    disabled_by: Optional[str] = None
    
    class Settings:
        name = "users"
```

### Game
```python
from beanie import Document
from pydantic import Field
from typing import Optional, List

class Game(Document):
    name: str = Field(min_length=3, max_length=30)
    short_description: str = Field(default="", max_length=200)
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    url: str

    class Settings:
        name = "games"
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

    class Settings:
        name = "cards"
```

### Score
```python
from beanie import Document, Link
from pydantic import Field
from typing import Optional

class Score(Document):
    game_id: Link[Game]
    user_id: Link[User]
    username: str
    score: int = Field(ge=0)
    created_at: Optional[str] = None
    
    class Settings:
        name = "scores"
```

## 애플리케이션 레벨(Backend↔Frontend)

> `schemas`라고도 불립니다.

### UserResponse
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    username: str
    disabled: bool = False
    is_admin: bool = False
    disabled_reason: Optional[str] = None
    disabled_at: Optional[datetime] = None
```

### UserCreate
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
```

### AccountAction
```python
from pydantic import BaseModel
from typing import Optional

class AccountAction(BaseModel):
    """계정 활성화/비활성화를 위한 요청 모델"""
    reason: Optional[str] = None
```

### AdminUserAction
```python
from pydantic import BaseModel
from typing import Optional

class AdminUserAction(BaseModel):
    """관리자의 사용자 관리 작업을 위한 요청 모델"""
    username: str
    reason: Optional[str] = None
```

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

### PasswordRequest
```python
from pydantic import BaseModel

class PasswordRequest(BaseModel):
    password: str
```

### UserListItem
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserListItem(BaseModel):
    """사용자 목록 항목"""
    username: str
    disabled: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    disabled_at: Optional[datetime]
    disabled_reason: Optional[str]
    disabled_by: Optional[str]
```

### UserFilter
```python
from pydantic import BaseModel
from typing import Optional

class UserFilter(BaseModel):
    """사용자 필터링 옵션"""
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None
    username_contains: Optional[str] = None
    limit: int = 50
    skip: int = 0
```

## 데이터 구조 사용 패턴 표

| 모델/스키마          | 타입        | 사용 위치                                   | 주요 기능                                                             |
|-----------------|-----------|-----------------------------------------|-------------------------------------------------------------------|
| User            | 데이터베이스 모델 | `src/backend/models/user.py`            | 사용자 정보 저장, 인증, 관리자 권한 확인                                          |
| Game            | 데이터베이스 모델 | `src/backend/models/game.py`            | 게임 정보 저장                                                          |
| Card            | 데이터베이스 모델 | `src/backend/models/game.py`            | 게임 관련 카드 정보 저장                                                    |
| UserResponse    | API 스키마   | `src/backend/schemas/authentication.py` | 사용자 정보 API 응답                                                     |
| UserCreate      | API 스키마   | `src/backend/schemas/authentication.py` | 회원가입 요청 처리 `/register`                                            |
| AccountAction   | API 스키마   | `src/backend/schemas/authentication.py` | 계정 활성화/비활성화 요청 처리 `/users/deactivate`                             |
| AdminUserAction | API 스키마   | `src/backend/schemas/authentication.py` | 관리자의 사용자 관리 작업 처리 `/admin/users/disable`, `/admin/users/enable` 등 |
| SearchResult    | API 스키마   | `src/backend/schemas/game_list.py`      | 게임 검색 결과 응답                                                       |
| CardResult      | API 스키마   | `src/backend/schemas/game_list.py`      | 게임 카드 정보 응답                                                       |
| PasswordRequest | API 스키마   | `src/backend/schemas/main.py`           | 비밀번호 처리 요청                                                        |
| UserListItem    | API 스키마   | `src/backend/authentication/admin.py`   | 관리자용 사용자 목록 조회 응답 `/admin/users/list`                             |
| UserFilter      | API 스키마   | `src/backend/authentication/admin.py`   | 사용자 목록 필터링 옵션 처리 `/admin/users/list`                              |

## 인증 관련 데이터 흐름

1. **회원가입 (`/register`)**
   - 클라이언트: `UserCreate` 스키마로 요청
   - 서버: `User` 모델로 데이터베이스에 저장
   - 응답: `UserResponse` 스키마로 반환

2. **로그인 (`/login`)**
   - 클라이언트: HTTP Basic 인증으로 요청
   - 서버: `User` 모델로 데이터베이스에서 조회
   - 응답: `UserResponse` 스키마로 반환

3. **내 정보 조회 (`/users/me`)**
   - 서버: `User` 모델로 데이터베이스에서 조회
   - 응답: `UserResponse` 스키마로 반환

4. **계정 비활성화 (`/users/deactivate`)**
   - 클라이언트: `AccountAction` 스키마로 요청
   - 서버: `User` 모델 업데이트
   - 응답: `UserResponse` 스키마로 반환

## 관리자 기능 데이터 흐름

1. **사용자 목록 조회 (`/admin/users/list`)**
   - 클라이언트: `UserFilter` 스키마로 요청
   - 서버: `User` 모델로 데이터베이스에서 조회
   - 응답: `UserListItem` 스키마 리스트로 반환

2. **사용자 관리 작업**
   - 클라이언트: `AdminUserAction` 스키마로 요청
   - 서버: `User` 모델 업데이트
   - 응답: `UserResponse` 스키마로 반환

