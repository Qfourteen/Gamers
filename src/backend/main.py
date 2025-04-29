from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import List

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.backend.schemas.game_list import SearchResult, CardResult
from src.backend.models.game import Game, Card
from src.backend.models.user import User

from src.backend.authentication.basic import basic_router

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

# 정적 파일 서빙: 프론트엔드 빌드 결과물을 사용
app.mount("/static", StaticFiles(directory="./static"), name="static")

templates = Jinja2Templates(directory="./templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return FileResponse("./static/index.html")


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