from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import createToken
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import LoginReq, LoginRes, SignUpReq, SignUpRes

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/signup", response_model=SignUpRes)
def signup(req: SignUpReq, db: Session = Depends(get_db)):
    email = req.email.strip()
    user = db.scalar(select(User).where(func.lower(func.trim(User.email)) == email.lower()))
    if user:
        print("Duplicate Registration")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    newUser = User(email=email, password=req.password, name=req.name)
    db.add(newUser)
    db.commit()
    return req

@router.post("/login", response_model=LoginRes)
def login(req: LoginReq, res: Response, db: Session = Depends(get_db)):
    # 회원 가입이 되어있는지 아닌지 확인
    email = req.email.strip()
    user = db.scalar(select(User).where(func.lower(func.trim(User.email)) == email.lower()))
    if user:
        if user.password == req.password:
            res.set_cookie(
                "EN_AT",
                createToken(user.email),
                httponly=True,
                secure=settings.KAKAO_REDIRECT_URI.startswith("https://"),
                samesite="lax"
            )
            print("Login Successful")
            return LoginRes(email=user.email)
    print("Login Failed")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
