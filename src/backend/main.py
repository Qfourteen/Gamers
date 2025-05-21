from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import List

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.backend.schemas.game_list import SearchResult, CardResult
from src.backend.schemas.main import PasswordRequest
from src.backend.models.game import Game, Card
from src.backend.models.user import User

from src.backend.authentication.basic import basic_router
from src.backend.authentication.admin import admin_router, api_router
from src.backend.authentication.game_admin import admin_game_router, api_game_router
from src.backend.utility.nickname_utils import is_valid_nickname, get_nickname_validation_rules
from src.backend.utility.password_utils import is_valid_password, get_password_strength, get_password_validation_rules

from src.backend.env import *
from src.backend.generate_dummy import get_data_card, get_data_search

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(client.gamers, document_models=[Game, Card, User])
    yield
    client.close()

app = FastAPI(lifespan=lifespan)

# 인증 라우터 추가
app.include_router(basic_router, prefix="/auth", tags=["authentication"])

# 관리자 라우터 추가
app.include_router(admin_router, tags=["admin"])
app.include_router(api_router, tags=["admin-api"])
app.include_router(admin_game_router, tags=["admin-games"])
app.include_router(api_game_router, tags=["admin-games-api"])

# 정적 파일 서빙: 프론트엔드 빌드 결과물을 사용
app.mount("/static", StaticFiles(directory="./static"), name="static")

templates = Jinja2Templates(directory="./templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return FileResponse("./static/index.html")

@app.get("/introduce", response_class=HTMLResponse)
async def introduce(request: Request):
    return FileResponse("./static/introduce.html")

@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request):
    return FileResponse("./static/policy.html")

@app.get("/data/search", response_model=List[SearchResult])
async def search_data(request: Request):
    """
    TODO: 카드 가져오는 올바른 로직이 필요함.
    :param request:
    :return:
    """
    result = get_data_search()
    return result


@app.get("/data/card", response_model=List[CardResult])
async def card_data(request: Request):
    """
    TODO: 카드 가져오는 올바른 로직이 필요함.
    :param request:
    :return:
    """
    result = get_data_card()
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
