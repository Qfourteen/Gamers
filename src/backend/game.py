from fastapi import APIRouter, HTTPException, status, Request, Depends
from starlette.responses import FileResponse
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from src.backend.models.game import Game, Score
from src.backend.models.user import User
from src.backend.schemas.game_list import ScoreCreate, ScoreResponse
from src.backend.authentication import get_current_user

from beanie.operators import And

game_router = APIRouter()

@game_router.get("/1944")
async def nineteenfourtyfour():
    return FileResponse("./static/game/1944.html")

@game_router.get("/endlessjump")
async def endless_jump():
    return FileResponse("./static/game/endlessjump.html")

@game_router.get("/no-more-floor")
async def no_more_floor():
    return FileResponse("./static/game/TJ.py")

@game_router.post("/api/scores", response_model=ScoreResponse)
async def create_score(
    score_data: ScoreCreate,
    current_user: User = Depends(get_current_user)
):
    """
    게임 점수를 저장합니다. 동일 사용자·게임에 기존 점수가 있는 경우,
    새 점수가 더 높을 때만 업데이트하고, 그렇지 않으면 기존 점수를 그대로 반환합니다.
    로그인된 사용자만 점수를 저장할 수 있습니다.
    """
    # 1) 게임 조회
    game = await Game.find_one(Game.url == score_data.game_url)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found for the provided URL"
        )

    # 2) 기존 점수 조회 (동일 user_id, game_id)
    existing: Optional[Score] = await Score.find_one(
        And(Score.game_id.id == game.id, Score.user_id.id == current_user.id)
    )

    # 현재 시간 문자열
    now_iso = datetime.now(timezone.utc).isoformat()

    # 3) 이미 점수가 존재하는 경우
    if existing:
        # 3-1) 새 점수가 더 높을 때만 업데이트
        if score_data.score > existing.score:
            existing.score = score_data.score
            existing.created_at = now_iso
            await existing.save()    # 변경사항 저장

            return ScoreResponse(
                id=str(existing.id),
                game_id=str(game.id),
                username=current_user.username,
                score=existing.score,
                created_at=existing.created_at
            )
        # 3-2) 그렇지 않으면 그대로 반환
        return ScoreResponse(
            id=str(existing.id),
            game_id=str(game.id),
            username=current_user.username,
            score=existing.score,
            created_at=existing.created_at
        )

    # 4) 기존 점수가 없는 경우 → 새로 생성
    score = Score(
        game_id=game,
        user_id=current_user,
        username=current_user.username,
        score=score_data.score,
        created_at=now_iso
    )
    await score.insert()

    return ScoreResponse(
        id=str(score.id),
        game_id=str(game.id),
        username=current_user.username,
        score=score.score,
        created_at=score.created_at
    )

@game_router.get("/api/scores", response_model=List[ScoreResponse])
async def get_high_scores(game_url: str, limit: int = 5):
    # 1) 게임 조회
    game = await Game.find_one(Game.url == game_url)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found for the provided URL"
        )

    # 2) Score 조회 + 링크된 User를 Prefetch
    scores = await Score.find(
        {"game_id.$id": ObjectId(game.id)}
    ).sort(-Score.score, -Score.created_at).limit(limit).to_list()

    # 3) 응답 변환
    return [
        ScoreResponse(
            id=str(score.id),
            game_id=str(score.game_id),
            username=score.username,
            score=score.score,
            created_at=score.created_at
        )
        for score in scores
    ]
