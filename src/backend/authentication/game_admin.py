from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
import os

from src.backend.models.game import Game, Card, Score
from src.backend.schemas.game_list import (
    GameCreate, GameUpdate, GameResponse,
    CardCreate, CardUpdate, CardResponse
)

from . import (
    get_current_user, check_admin_permissions
)

admin_game_router = APIRouter(prefix="/admin/games")
api_game_router = APIRouter(prefix="/api/admin/games")

# 템플릿 디렉토리 설정
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Game CRUD API Endpoints
@api_game_router.post("", response_model=GameResponse)
async def create_game(
    game_data: GameCreate,
    request: Request
):
    """
    관리자가 새 게임을 생성합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    # 게임 생성
    now = datetime.now(timezone.utc).isoformat()
    game = Game(
        name=game_data.name,
        short_description=game_data.short_description,
        description=game_data.description,
        tags=game_data.tags,
        url=game_data.url,
        created_at=now,
        updated_at=now,
        created_by=current_user.username
    )
    await game.insert()
    
    return GameResponse(
        id=str(game.id),
        name=game.name,
        short_description=game.short_description,
        description=game.description,
        tags=game.tags,
        url=game.url,
        created_at=game.created_at,
        updated_at=game.updated_at,
        created_by=game.created_by
    )

@api_game_router.get("", response_model=List[GameResponse])
async def list_games(
    request: Request,
    limit: int = 50,
    skip: int = 0
):
    """
    관리자가 게임 목록을 조회합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    games = await Game.find().sort(-Game.created_at).skip(skip).limit(limit).to_list()
    
    return [
        GameResponse(
            id=str(game.id),
            name=game.name,
            short_description=game.short_description,
            description=game.description,
            tags=game.tags,
            url=game.url,
            created_at=game.created_at,
            updated_at=game.updated_at,
            created_by=game.created_by
        ) for game in games
    ]

@api_game_router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: str,
    request: Request
):
    """
    관리자가 특정 게임을 조회합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    game = await Game.get(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    return GameResponse(
        id=str(game.id),
        name=game.name,
        short_description=game.short_description,
        description=game.description,
        tags=game.tags,
        url=game.url,
        created_at=game.created_at,
        updated_at=game.updated_at,
        created_by=game.created_by
    )

@api_game_router.put("/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: str,
    game_data: GameUpdate,
    request: Request
):
    """
    관리자가 게임 정보를 업데이트합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    game = await Game.get(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # 업데이트할 필드만 갱신
    update_data = game_data.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await game.update({"$set": update_data})
    
    # 갱신된 게임 조회
    game = await Game.get(game_id)
    
    return GameResponse(
        id=str(game.id),
        name=game.name,
        short_description=game.short_description,
        description=game.description,
        tags=game.tags,
        url=game.url,
        created_at=game.created_at,
        updated_at=game.updated_at,
        created_by=game.created_by
    )

@api_game_router.delete("/{game_id}", response_model=dict)
async def delete_game(
    game_id: str,
    request: Request
):
    """
    관리자가 게임을 삭제합니다. 관련된 카드도 함께 삭제됩니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    game = await Game.get(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # 게임 관련 카드 삭제
    await Card.find({"game_id.$id": ObjectId(game.id)}).delete_many()
    
    # 게임 관련 점수 삭제
    await Score.find({"game_id.$id": ObjectId(game.id)}).delete_many()
    
    # 게임 삭제
    await game.delete()
    
    return {"message": "Game, its cards, and scores deleted successfully"}

# Card CRUD API Endpoints
@api_game_router.post("/cards", response_model=CardResponse)
async def create_card(
    card_data: CardCreate,
    request: Request
):
    """
    관리자가 새 카드를 생성합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    # 연결된 게임 확인
    game = await Game.get(card_data.game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # 카드 생성
    now = datetime.now(timezone.utc).isoformat()
    card = Card(
        game_id=game,
        card_body=card_data.card_body,
        image_base64=card_data.image_base64,
        card_title=card_data.card_title,
        created_at=now,
        updated_at=now,
        created_by=current_user.username
    )
    await card.insert()
    
    return CardResponse(
        id=str(card.id),
        game_id=str(card.game_id.id),
        card_body=card.card_body,
        image_base64=card.image_base64,
        card_title=card.card_title,
        created_at=card.created_at,
        updated_at=card.updated_at,
        created_by=card.created_by
    )

@api_game_router.get("/cards/{game_id}", response_model=List[CardResponse])
async def list_cards_by_game(
    game_id: str,
    request: Request,
    limit: int = 50,
    skip: int = 0
):
    """
    관리자가 특정 게임의 카드 목록을 조회합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    # 게임 존재 확인
    game = await Game.get(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # 해당 게임의 카드 조회
    cards = await Card.find({"game_id.$id": ObjectId(game.id)}).sort(-Card.created_at).skip(skip).limit(limit).to_list()
    
    return [
        CardResponse(
            id=str(card.id),
            game_id=str(card.game_id.id),
            card_body=card.card_body,
            image_base64=card.image_base64,
            card_title=card.card_title,
            created_at=card.created_at,
            updated_at=card.updated_at,
            created_by=card.created_by
        ) for card in cards
    ]

@api_game_router.put("/cards/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: str,
    card_data: CardUpdate,
    request: Request
):
    """
    관리자가 카드 정보를 업데이트합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)

    card = await Card.get(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )

    # 업데이트할 필드만 갱신
    update_data = card_data.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await card.update({"$set": update_data})

    # 갱신된 카드와 링크된 게임 정보까지 다시 조회
    card = await Card.get(card_id, fetch_links=True)

    return CardResponse(
        id=str(card.id),
        game_id=str(card.game_id.id),  # 또는 필요하면 card.game_id.name 등
        card_body=card.card_body,
        image_base64=card.image_base64,
        card_title=card.card_title,
        created_at=card.created_at,
        updated_at=card.updated_at,
        created_by=card.created_by
    )


@api_game_router.delete("/cards/{card_id}", response_model=dict)
async def delete_card(
    card_id: str,
    request: Request
):
    """
    관리자가 카드를 삭제합니다.
    """
    current_user = await get_current_user(request)
    await check_admin_permissions(current_user)
    
    card = await Card.get(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # 카드 삭제
    await card.delete()
    
    return {"message": "Card deleted successfully"}

# 관리자 웹 인터페이스 라우트
@admin_game_router.get("", response_class=HTMLResponse)
async def admin_games_page(
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    관리자 게임 관리 페이지를 제공합니다.
    """
    await check_admin_permissions(current_user)
    
    games = await Game.find().sort(-Game.created_at).to_list()
    
    return templates.TemplateResponse(
        "admin/games.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "games",
            "games": games,
            "messages": []
        }
    )

@admin_game_router.get("/{game_id}", response_class=HTMLResponse)
async def admin_game_detail_page(
    game_id: str,
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    관리자 게임 상세 및 카드 관리 페이지를 제공합니다.
    """
    await check_admin_permissions(current_user)
    
    game = await Game.get(game_id)
    if not game:
        return RedirectResponse(url="/admin/games", status_code=303)
    
    cards = await Card.find({"game_id.$id": ObjectId(game.id)}).sort(-Card.created_at).to_list()
    
    return templates.TemplateResponse(
        "admin/game_detail.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "games",
            "game": game,
            "cards": cards,
            "messages": []
        }
    )