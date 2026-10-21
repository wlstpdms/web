from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from pathlib import Path

from app.api.routers import board, clothing_payments, kakao_auth, language, user
from app.db.database import Base, engine
from app.models.board import Board
from app.models.user import User
from app.models.social_account import SocialAccount
from app.models.language import Lesson, LessonStep, LearningProgress, StudyGroup, GroupMember, UserEntitlement, LearningActivity
from app.models.payment import ClothingOrder, PlanOrder

app = FastAPI(title="노트 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://www.my-do.kro.kr",
        "https://www.my-do.kro.kr",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Accept both the public /api path and the path after nginx strips /api
# (for example, with `proxy_pass http://backend/;`).
app.include_router(user.router, prefix="/api")
app.include_router(kakao_auth.router, prefix="/api")
app.include_router(board.router, prefix="/api")
app.include_router(language.router, prefix="/api")
app.include_router(language.frontend_router, prefix="/api")
app.include_router(clothing_payments.router, prefix="/api")
app.include_router(user.router)
app.include_router(kakao_auth.router)
app.include_router(board.router)
app.include_router(language.router)
app.include_router(language.frontend_router)
app.include_router(clothing_payments.router)

Base.metadata.create_all(bind=engine)

# create_all does not add columns to tables that already exist. Keep older local
# databases compatible with the optional product photo URL field.
if "board" in inspect(engine).get_table_names():
    board_columns = {column["name"] for column in inspect(engine).get_columns("board")}
    if "image_url" not in board_columns:
        with engine.begin() as connection:
            connection.exec_driver_sql("ALTER TABLE board ADD COLUMN image_url VARCHAR")

product_media = Path(__file__).resolve().parent.parent / "uploads" / "products"
product_media.mkdir(parents=True, exist_ok=True)
app.mount("/api/media", StaticFiles(directory=product_media), name="product-media")

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
frontend_index = frontend_dist / "index.html"
doji_index = frontend_dist / "doji.html"

if frontend_index.is_file():
    @app.get("/", include_in_schema=False)
    def frontend_home():
        return FileResponse(frontend_index)

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_routes(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        if full_path == "posts" or full_path.startswith("posts/"):
            if doji_index.is_file():
                return FileResponse(doji_index)
            raise HTTPException(status_code=503, detail="DOJI frontend build is missing")

        asset = (frontend_dist / full_path).resolve()
        if asset.is_relative_to(frontend_dist.resolve()) and asset.is_file():
            return FileResponse(asset)
        return FileResponse(frontend_index)
