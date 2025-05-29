from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from difflib import SequenceMatcher
from typing import List

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.backend.schemas.game_list import SearchResult, CardResult
from src.backend.schemas.main import PasswordRequest
from src.backend.models.game import Game, Card, Score
from src.backend.models.user import User

from src.backend.authentication.basic import basic_router
from src.backend.authentication.admin import admin_router, api_router
from src.backend.authentication.game_admin import admin_game_router, api_game_router
from src.backend.authentication import get_current_user, check_admin_permissions
from src.backend.game import game_router
from src.backend.utility.nickname_utils import is_valid_nickname, get_nickname_validation_rules
from src.backend.utility.password_utils import is_valid_password, get_password_strength, get_password_validation_rules

from src.backend.env import *
from src.backend.generate_dummy import get_data_card, get_data_search

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(client.gamers, document_models=[Game, Card, User, Score])
    yield
    client.close()

app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# 인증 라우터 추가
app.include_router(basic_router, prefix="/auth", tags=["authentication"])

# 관리자 라우터 추가
app.include_router(admin_router, tags=["admin"])
app.include_router(api_router, tags=["admin-api"])
app.include_router(admin_game_router, tags=["admin-games"])
app.include_router(api_game_router, tags=["admin-games-api"])
app.include_router(game_router, prefix="/games", tags=["game-list"])

# 정적 파일 서빙: 프론트엔드 빌드 결과물을 사용
app.mount("/static", StaticFiles(directory="./static"), name="static")

templates = Jinja2Templates(directory="./templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return FileResponse("./static/react/index.html")

@app.get("/introduce", response_class=HTMLResponse)
async def introduce(request: Request):
    return FileResponse("./static/introduce.html")

@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request):
    return FileResponse("./static/policy.html")


def similarity(a: str, b: str) -> float:
    """두 문자열의 유사도를 계산합니다 (0.0 ~ 1.0)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def korean_similarity_search(text: str, query: str) -> float:
    """한국어 텍스트에서 쿼리와의 유사도를 계산합니다"""
    if not text or not query:
        return 0.0

    # 완전 일치 검사
    if query in text:
        return 1.0

    # 부분 문자열 유사도 검사
    max_similarity = 0.0
    words = text.split()

    for word in words:
        sim = similarity(word, query)
        max_similarity = max(max_similarity, sim)

    # 전체 텍스트 유사도도 고려
    full_sim = similarity(text, query)

    return max(max_similarity, full_sim)

@app.get("/data/search", response_model=List[SearchResult])
async def search_data(request: Request, q: str = ""):
    """
    한국어 유사도 기반 게임 검색을 수행합니다.
    :param request:
    :param q: 검색 쿼리
    :return:
    """
    if not q.strip():
        return []

    if len(q) > 100:
        return []

    games = await Game.find_all().to_list()
    search_results = []
    
    for game in games:
        # 이름, 짧은 설명, 설명, 태그에서 검색
        name_score = korean_similarity_search(game.name, q)
        short_desc_score = korean_similarity_search(game.short_description, q)
        desc_score = korean_similarity_search(game.description, q)
        
        # 태그 검색
        tag_score = 0.0
        for tag in game.tags:
            tag_sim = korean_similarity_search(tag, q)
            tag_score = max(tag_score, tag_sim)
        
        # 최종 점수 계산 (가중치 적용)
        final_score = max(
            name_score * 1.5,  # 이름은 가중치 높게
            short_desc_score * 1.2,
            desc_score,
            tag_score * 1.3  # 태그도 가중치 높게
        )
        
        # 유사도 임계값 (0.3 이상)
        if final_score >= 0.3:
            search_results.append({
                'game': game,
                'score': final_score
            })
    
    # 점수 순으로 정렬
    search_results.sort(key=lambda x: x['score'], reverse=True)
    
    # SearchResult 객체로 변환
    result = []
    for item in search_results:
        game = item['game']
        result.append(SearchResult(
            name=game.name,
            short_description=game.short_description,
            tags=game.tags,
            game_id=str(game.id)
        ))
    
    return result


@app.get("/data/card", response_model=List[CardResult])
async def card_data(request: Request):
    """
    카드 데이터 4개를 랜덤으로 가져옵니다.
    :param request:
    :return:
    """
    import random
    
    cards = await Card.find_all().to_list()
    if len(cards) >= 4:
        random_cards = random.sample(cards, 4)
    else:
        random_cards = cards
    
    result = []
    for card in random_cards:
        game = await card.game_id.fetch()
        result.append(CardResult(
            name=game.name,
            image_base64=card.image_base64,
            card_title=card.card_title,
            game_id=str(card.game_id.ref.id)
        ))
    
    return result


@app.get("/auth/validate-nickname")
async def validate_nickname(nickname: str):
    """
    입력받은 닉네임이 유효한지 검증합니다.
    
    Args:
        nickname (str): 검증할 닉네임
        
    Returns:
        dict: 닉네임 유효성 여부와 오류 메시지(해당될 경우)
    """
    valid = is_valid_nickname(nickname)
    return {
        "valid": valid,
        "message": "유효한 닉네임입니다." if valid else "유효하지 않은 닉네임입니다."
    }


@app.get("/auth/nickname-rules")
async def get_nickname_rules():
    """
    닉네임 생성 규칙을 반환합니다.
    
    Returns:
        dict: 닉네임 생성 규칙
    """
    return get_nickname_validation_rules()


@app.post("/auth/validate-password")
async def validate_password(request: PasswordRequest):
    """
    입력받은 비밀번호가 유효한지 검증하고 강도 정보를 반환합니다.
    
    POST 방식을 사용하여 보안을 강화합니다.
    
    Request Body:
        password (str): 검증할 비밀번호
        
    Returns:
        dict: 비밀번호 강도 정보와 유효성 여부
    """
    return get_password_strength(request.password)


@app.get("/auth/password-rules")
async def get_password_rules():
    """
    비밀번호 생성 규칙을 반환합니다.
    
    Returns:
        dict: 비밀번호 생성 규칙
    """
    return get_password_validation_rules()


async def check_admin_user(request: Request):
    """
    현재 사용자가 관리자인지 확인하는 헬퍼 함수
    """
    try:
        user = await get_current_user(request)
        await check_admin_permissions(user)
        return user
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@app.get("/docs", include_in_schema=False)
async def admin_docs(request: Request):
    """
    관리자 전용 API 문서
    """
    await check_admin_user(request)
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Gamers API - Admin Documentation"
    )


@app.get("/redoc", include_in_schema=False)
async def admin_redoc(request: Request):
    """
    관리자 전용 ReDoc 문서
    """
    await check_admin_user(request)
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Gamers API - Admin Documentation"
    )


@app.get("/openapi.json", include_in_schema=False)
async def admin_openapi(request: Request):
    """
    관리자 전용 OpenAPI 스키마
    """
    await check_admin_user(request)
    return JSONResponse(app.openapi())
