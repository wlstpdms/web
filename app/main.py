from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.api.routers import board, user
from app.db.database import Base, engine
from app.models.board import Board
from app.models.user import User

app = FastAPI(title="노트 API", version="0.1.0")

# Accept both the public /api path and the path after nginx strips /api
# (for example, with `proxy_pass http://backend/;`).
app.include_router(user.router, prefix="/api")
app.include_router(board.router, prefix="/api")
app.include_router(user.router)
app.include_router(board.router)

Base.metadata.create_all(bind=engine)

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
frontend_index = frontend_dist / "index.html"

if frontend_index.is_file():
    @app.get("/", include_in_schema=False)
    def frontend_home():
        return FileResponse(frontend_index)

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_routes(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        asset = (frontend_dist / full_path).resolve()
        if asset.is_relative_to(frontend_dist.resolve()) and asset.is_file():
            return FileResponse(asset)
        return FileResponse(frontend_index)
