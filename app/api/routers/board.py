from sqlalchemy.orm import Session
from app.db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.models.board import Board
from app.schemas.board import RegisterReq, RegisterRes, ReadRes
from sqlalchemy import select
from pathlib import Path
from uuid import uuid4

router = APIRouter(prefix="/board", tags=["board"])
PRODUCT_IMAGE_DIR = Path(__file__).resolve().parents[3] / "uploads" / "products"
MAX_IMAGE_SIZE = 8 * 1024 * 1024

@router.post("/images")
async def upload_product_image(request: Request):
    media_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    extensions = {"image/jpeg": ("jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
                  "image/png": ("png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
                  "image/webp": ("webp", lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP")}
    if media_type not in extensions:
        raise HTTPException(status_code=415, detail="JPG, PNG, WEBP 이미지 파일만 등록할 수 있어요.")
    if int(request.headers.get("content-length", "0") or 0) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="이미지는 8MB 이하로 올려 주세요.")
    image = await request.body()
    if not image or len(image) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="이미지는 8MB 이하로 올려 주세요.")
    extension, matches_signature = extensions[media_type]
    if not matches_signature(image):
        raise HTTPException(status_code=415, detail="파일 형식이 이미지와 일치하지 않아요.")
    PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{extension}"
    (PRODUCT_IMAGE_DIR / filename).write_bytes(image)
    return {"image_url": f"/api/media/products/{filename}"}

@router.post("/register", response_model=RegisterRes)
def register(req: RegisterReq, db: Session = Depends(get_db)):
    board = Board(title=req.title, contents=req.contents, image_url=req.image_url)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board

@router.get("/read/{idx}", response_model=ReadRes)
def read(idx: int, db: Session = Depends(get_db)):
    board = db.get(Board, idx)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return board

@router.get("/list", response_model=list[ReadRes])
def list_boards(db: Session = Depends(get_db)):
    return db.scalars(select(Board).order_by(Board.idx.desc())).all()
