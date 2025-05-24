from fastapi import APIRouter
from starlette.responses import FileResponse

game_router = APIRouter()

@game_router.get("/1944")
async def nineteenfourtyfour():
    return FileResponse("./static/game/1944.html")
