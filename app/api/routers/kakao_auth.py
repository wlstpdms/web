import hashlib
import hmac
import json
import secrets
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest, urlopen

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import createToken
from app.db.database import get_db
from app.models.social_account import SocialAccount
from app.models.user import User

router = APIRouter(prefix="/user/kakao", tags=["user"])


class KakaoCodeReq(BaseModel):
    code: str
    state: str


class KakaoStateRes(BaseModel):
    state: str


class KakaoLoginRes(BaseModel):
    name: str


def _make_kakao_state() -> str:
    issued_at = str(int(time.time()))
    nonce = secrets.token_urlsafe(24)
    message = f"{issued_at}.{nonce}"
    signature = hmac.new(settings.SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{message}.{signature}"


def _valid_kakao_state(state: str) -> bool:
    try:
        issued_at, nonce, signature = state.split(".", 2)
        age = int(time.time()) - int(issued_at)
        if age < 0 or age > 600 or not nonce:
            return False
        message = f"{issued_at}.{nonce}"
        expected = hmac.new(settings.SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
    except (ValueError, TypeError):
        return False


def _set_kakao_state_cookie(res: Response, state: str) -> None:
    res.set_cookie(
        "KAKAO_OAUTH_STATE",
        state,
        httponly=True,
        secure=settings.KAKAO_REDIRECT_URI.startswith("https://"),
        samesite="lax",
        max_age=600,
        path="/",
    )


def _kakao_request(url: str, *, data: bytes | None = None, access_token: str | None = None) -> dict:
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded;charset=utf-8"
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    request = UrlRequest(url, data=data, headers=headers)
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Kakao authentication could not be verified. Please try again.") from exc


@router.get("/state", response_model=KakaoStateRes)
def kakao_state(res: Response):
    if not settings.KAKAO_REST_API_KEY:
        raise HTTPException(status_code=503, detail="Kakao login is not configured.")
    state = _make_kakao_state()
    _set_kakao_state_cookie(res, state)
    return KakaoStateRes(state=state)


@router.get("/authorize", response_class=RedirectResponse)
def kakao_authorize():
    if not settings.KAKAO_REST_API_KEY:
        raise HTTPException(status_code=503, detail="Kakao login is not configured.")
    state = _make_kakao_state()
    params = urlencode(
        {
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "response_type": "code",
            "state": state,
            "scope": "profile_nickname",
        }
    )
    response = RedirectResponse(url=f"https://kauth.kakao.com/oauth/authorize?{params}", status_code=302)
    _set_kakao_state_cookie(response, state)
    return response


@router.post("/callback", response_model=KakaoLoginRes)
def kakao_callback(
    req: KakaoCodeReq,
    request: Request,
    res: Response,
    db: Session = Depends(get_db),
):
    if not settings.KAKAO_REST_API_KEY:
        raise HTTPException(status_code=503, detail="Kakao login is not configured.")
    if not _valid_kakao_state(req.state) or not hmac.compare_digest(
        req.state, request.cookies.get("KAKAO_OAUTH_STATE", "")
    ):
        raise HTTPException(status_code=400, detail="Kakao login request expired or is invalid.")
    res.delete_cookie("KAKAO_OAUTH_STATE", path="/")

    token_params = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": req.code,
    }
    if settings.KAKAO_CLIENT_SECRET:
        token_params["client_secret"] = settings.KAKAO_CLIENT_SECRET
    token = _kakao_request(
        "https://kauth.kakao.com/oauth/token",
        data=urlencode(token_params).encode(),
    )
    access_token = token.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Kakao authentication failed. Please try again.")

    profile = _kakao_request("https://kapi.kakao.com/v2/user/me", access_token=access_token)
    kakao_id = profile.get("id")
    account = profile.get("kakao_account") or {}
    nickname = (
        (account.get("profile") or {}).get("nickname")
        or (profile.get("properties") or {}).get("nickname")
        or ""
    ).strip()
    if not kakao_id:
        raise HTTPException(status_code=401, detail="Could not read the Kakao user profile.")
    if not nickname:
        raise HTTPException(status_code=403, detail="Kakao did not return a nickname. Check the nickname consent setting.")

    social = db.scalar(
        select(SocialAccount).where(
            SocialAccount.provider == "kakao",
            SocialAccount.provider_user_id == str(kakao_id),
        )
    )
    if social:
        user = db.get(User, social.user_idx)
        if not user:
            raise HTTPException(status_code=401, detail="The linked account could not be found.")
        user.name = nickname
    else:
        user = User(
            # User requires an email; Kakao identity is keyed by provider_user_id.
            email=f"kakao-{kakao_id}@users.invalid",
            password=secrets.token_urlsafe(48),
            name=nickname,
        )
        db.add(user)
        db.flush()
        db.add(SocialAccount(provider="kakao", provider_user_id=str(kakao_id), user_idx=user.idx))

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Could not process the Kakao account. Please log in again.") from exc

    res.set_cookie(
        "EN_AT",
        createToken(user.email),
        httponly=True,
        secure=settings.KAKAO_REDIRECT_URI.startswith("https://"),
        samesite="lax",
    )
    return KakaoLoginRes(name=user.name)
