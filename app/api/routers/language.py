from datetime import date, datetime, timedelta, timezone
import secrets
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.language import (
    GroupMember, LearningActivity, LearningProgress, Lesson, LessonStep,
    StudyGroup, UserEntitlement,
)
from app.models.user import User
from app.models.payment import PlanOrder

router = APIRouter(prefix="/language", tags=["language"])
frontend_router = APIRouter(tags=["learning", "study groups", "billing"])

PRODUCTS = {
    "premium_monthly": {
        "id": "premium_monthly", "name": "말랑 플러스 월간", "price": 9900,
        "currency": "KRW", "interval": "month", "duration_days": 30,
        "description": "매달 가볍게 결제하고 모든 학습 기능을 이용해요.",
        "badge": "인기", "saving": None,
        "features": ["모든 프리미엄 레슨", "무제한 말하기 연습", "상세 학습 리포트", "광고 없이 학습"],
    },
    "premium_quarterly": {
        "id": "premium_quarterly", "name": "말랑 플러스 3개월", "price": 26900,
        "currency": "KRW", "interval": "quarter", "duration_days": 90,
        "description": "한 계절 동안 꾸준히 공부하는 분께 추천해요.",
        "badge": None, "saving": "월간보다 약 10% 절약",
        "features": ["모든 프리미엄 레슨", "무제한 말하기 연습", "상세 학습 리포트", "광고 없이 학습"],
    },
    "premium_yearly": {
        "id": "premium_yearly", "name": "말랑 플러스 연간", "price": 79000,
        "currency": "KRW", "interval": "year", "duration_days": 365,
        "description": "한 해의 학습 습관을 꾸준히 이어가요.",
        "badge": "가장 알뜰해요", "saving": "월간보다 약 33% 절약",
        "features": ["모든 프리미엄 레슨", "무제한 말하기 연습", "상세 학습 리포트", "광고 없이 학습", "연간 학습 요약"],
    },
}


def current_user(request: Request, db: Session) -> User:
    token = request.cookies.get("EN_AT")
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    try:
        email = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]).get("sub")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired login") from exc
    user = db.scalar(select(User).where(func.lower(User.email) == str(email).lower()))
    if user is None:
        raise HTTPException(status_code=401, detail="Account not found")
    return user


def optional_user(request: Request, db: Session) -> User | None:
    if not request.cookies.get("EN_AT"):
        return None
    try:
        return current_user(request, db)
    except HTTPException:
        return None


def entitlement(db: Session, user_idx: int) -> UserEntitlement:
    item = db.get(UserEntitlement, user_idx)
    if item is None:
        item = UserEntitlement(user_idx=user_idx, plan="free", ad_credits=0)
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


def seed_catalog(db: Session) -> None:
    if db.scalar(select(Lesson.id).limit(1)):
        return
    rows = [
        ("카페에서 주문하기", "beginner", "travel", False, [("아이스 아메리카노 한 잔 주세요.", "An iced Americano, please.", "주문할 때 please를 붙이면 자연스러워요."), ("포장해 주실 수 있나요?", "Could I get that to go?", "to go는 포장을 뜻해요.")]),
        ("가벼운 안부 묻기", "beginner", "conversation", False, [("주말은 어땠어요?", "How was your weekend?", "과거의 경험을 물을 때 How was를 사용해요."), ("요즘 영어를 공부하고 있어요.", "I'm studying English these days.", "these days는 요즘이라는 뜻이에요.")]),
        ("회의에서 의견 말하기", "intermediate", "work", True, [("제안 하나 드려도 될까요?", "Could I make a suggestion?", "정중하게 발언을 시작하는 표현이에요.")]),
    ]
    for order, (title, level, category, premium, steps) in enumerate(rows, 1):
        lesson = Lesson(title=title, level=level, category=category, duration_minutes=5, is_premium=int(premium), order=order)
        db.add(lesson)
        db.flush()
        for step_order, (prompt, answer, explanation) in enumerate(steps, 1):
            db.add(LessonStep(lesson_id=lesson.id, kind="phrase", prompt_ko=prompt, answer_en=answer, explanation_ko=explanation, order=step_order))
    db.commit()


def lesson_data(lesson: Lesson, progress: LearningProgress | None = None) -> dict:
    return {"id": lesson.id, "title": lesson.title, "level": lesson.level, "category": lesson.category,
            "duration_minutes": lesson.duration_minutes, "premium": bool(lesson.is_premium),
            "progress": {"completed_steps": progress.completed_steps, "total_steps": progress.total_steps, "status": progress.status} if progress else None}


@router.get("/lessons")
def list_lessons(request: Request, level: str | None = None, db: Session = Depends(get_db)):
    seed_catalog(db)
    query = select(Lesson).order_by(Lesson.order)
    if level:
        query = query.where(Lesson.level == level)
    user = optional_user(request, db)
    progress = {p.lesson_id: p for p in db.scalars(select(LearningProgress).where(LearningProgress.user_idx == user.idx)).all()} if user else {}
    return {"items": [lesson_data(row, progress.get(row.id)) for row in db.scalars(query).all()]}


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    seed_catalog(db)
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    plan = entitlement(db, user.idx)
    if lesson.is_premium and entitlement_data(plan)["plan"] != "premium":
        raise HTTPException(403, detail={"code": "premium_required", "message": "Premium plan required"})
    steps = db.scalars(select(LessonStep).where(LessonStep.lesson_id == lesson_id).order_by(LessonStep.order)).all()
    return {**lesson_data(lesson), "steps": [{"id": s.id, "kind": s.kind, "prompt_ko": s.prompt_ko, "answer_en": s.answer_en, "explanation_ko": s.explanation_ko, "order": s.order} for s in steps]}


class ProgressReq(BaseModel):
    completed_steps: int = Field(ge=0)
    total_steps: int = Field(ge=1)


@router.put("/lessons/{lesson_id}/progress")
def update_progress(lesson_id: int, req: ProgressReq, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    seed_catalog(db)
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    if req.completed_steps > req.total_steps:
        raise HTTPException(422, "completed_steps cannot exceed total_steps")
    row = db.scalar(select(LearningProgress).where(LearningProgress.user_idx == user.idx, LearningProgress.lesson_id == lesson_id))
    if row is None:
        row = LearningProgress(user_idx=user.idx, lesson_id=lesson_id)
        db.add(row)
    was_complete = row.status == "completed"
    row.completed_steps, row.total_steps = req.completed_steps, req.total_steps
    row.status = "completed" if req.completed_steps == req.total_steps else "in_progress"
    if row.status == "completed" and not was_complete:
        today = date.today().isoformat()
        activity = db.scalar(select(LearningActivity).where(LearningActivity.user_idx == user.idx, LearningActivity.activity_date == today))
        if activity is None:
            activity = LearningActivity(user_idx=user.idx, activity_date=today)
            db.add(activity)
        activity.xp += 20
        activity.minutes += lesson.duration_minutes
    db.commit()
    return {"lesson_id": lesson_id, "completed_steps": row.completed_steps, "total_steps": row.total_steps, "status": row.status, "xp_awarded": 20 if row.status == "completed" and not was_complete else 0}


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    seed_catalog(db)
    user = optional_user(request, db)
    if user is None:
        next_lesson = db.scalar(select(Lesson).where(Lesson.is_premium == 0).order_by(Lesson.order))
        groups = []
        return {"user": {"display_name": "학습자", "level": "beginner"}, "progress": {"streak_days": 0, "xp": 0, "weekly": []},
                "next_lesson": {"id": next_lesson.id, "title": next_lesson.title, "subtitle": next_lesson.category, "duration_minutes": next_lesson.duration_minutes, "xp_reward": 20} if next_lesson else None,
                "groups": groups, "credits": {"available": 0, "daily_limit": 3}, "subscription": {"plan": "free", "trial_days_left": 0}}
    plan = entitlement(db, user.idx)
    today = date.today().isoformat()
    activities = db.scalars(select(LearningActivity).where(LearningActivity.user_idx == user.idx).order_by(LearningActivity.activity_date.desc())).all()
    today_activity = next((a for a in activities if a.activity_date == today), None)
    active_dates = {a.activity_date for a in activities if a.xp > 0}
    streak = 0
    check_day = date.today()
    while check_day.isoformat() in active_dates:
        streak += 1
        check_day -= timedelta(days=1)
    completed = db.scalar(select(func.count()).select_from(LearningProgress).where(LearningProgress.user_idx == user.idx, LearningProgress.status == "completed")) or 0
    group_count = db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.user_idx == user.idx)) or 0
    week_start = date.today() - timedelta(days=6)
    weekly_map = {a.activity_date: a.xp for a in activities if a.activity_date >= week_start.isoformat()}
    weekly = [{"day": (week_start + timedelta(days=i)).isoformat(), "xp": weekly_map.get((week_start + timedelta(days=i)).isoformat(), 0)} for i in range(7)]
    groups = db.scalars(select(StudyGroup).join(GroupMember).where(GroupMember.user_idx == user.idx).order_by(StudyGroup.created_at.desc())).all()
    next_lesson = db.scalar(select(Lesson).where(Lesson.is_premium == 0).order_by(Lesson.order))
    trial_end = plan.trial_ends_at
    if trial_end and trial_end.tzinfo is None:
        trial_end = trial_end.replace(tzinfo=timezone.utc)
    trial_days = max(0, (trial_end - datetime.now(timezone.utc)).days) if trial_end and trial_end > datetime.now(timezone.utc) else 0
    return {"user": {"display_name": user.name, "level": "beginner"}, "progress": {"streak_days": streak, "xp": sum(a.xp for a in activities), "weekly": weekly},
            "next_lesson": {"id": next_lesson.id, "title": next_lesson.title, "subtitle": next_lesson.category, "duration_minutes": next_lesson.duration_minutes, "xp_reward": 20} if next_lesson else None,
            "groups": [{"id": g.id, "name": g.name, "members": db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == g.id)) or 0, "activity": "함께 영어를 공부해요"} for g in groups],
            "credits": {"available": plan.ad_credits, "daily_limit": 3}, "subscription": {"plan": "premium" if entitlement_data(plan)["plan"] == "premium" else "free", "trial_days_left": trial_days}}


# Frontend contract aliases; all paths are exposed with and without /api by app.main.
@frontend_router.get("/learning/dashboard")
def learning_dashboard(request: Request, db: Session = Depends(get_db)):
    return dashboard(request, db)


@frontend_router.get("/learning/lessons")
def learning_lessons(request: Request, db: Session = Depends(get_db)):
    return list_lessons(request, None, db)


@frontend_router.get("/learning/lessons/{lesson_id}")
def learning_lesson(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    return get_lesson(lesson_id, request, db)


@frontend_router.post("/learning/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    step_count = db.scalar(select(func.count()).select_from(LessonStep).where(LessonStep.lesson_id == lesson_id)) or 1
    result = update_progress(lesson_id, ProgressReq(completed_steps=step_count, total_steps=step_count), request, db)
    plan = entitlement(db, user.idx)
    activities = db.scalars(select(LearningActivity).where(LearningActivity.user_idx == user.idx).order_by(LearningActivity.activity_date.desc())).all()
    active = {a.activity_date for a in activities if a.xp > 0}
    check_day, streak = date.today(), 0
    while check_day.isoformat() in active:
        streak += 1
        check_day -= timedelta(days=1)
    return {"xp_earned": result["xp_awarded"], "streak_days": streak, "credits": plan.ad_credits}


@frontend_router.get("/study-groups")
def frontend_groups(request: Request, db: Session = Depends(get_db)):
    if optional_user(request, db) is None:
        return {"items": []}
    return list_groups(request, db)


@frontend_router.post("/study-groups", status_code=201)
def frontend_create_group(req: GroupCreateReq, request: Request, db: Session = Depends(get_db)):
    return create_group(req, request, db)


@frontend_router.get("/billing/plans")
def frontend_plans():
    return plans()


class CheckoutReq(BaseModel):
    plan_id: str = "premium_monthly"


@frontend_router.post("/billing/checkout")
def frontend_checkout(req: CheckoutReq, request: Request, db: Session = Depends(get_db)):
    if req.plan_id not in PRODUCTS:
        raise HTTPException(422, "Unsupported plan")
    user = current_user(request, db)
    if not settings.PORTONE_STORE_ID or not settings.PORTONE_CHANNEL_KEY:
        raise HTTPException(503, "PortOne Store ID and Toss Payments channel key are not configured")
    product = PRODUCTS[req.plan_id]
    payment_id = f"plan-{user.idx}-{secrets.token_urlsafe(18)}"
    db.add(PlanOrder(payment_id=payment_id, user_idx=user.idx, plan_id=req.plan_id, amount=product["price"]))
    db.commit()
    return {"payment_id": payment_id, "order_name": product["name"], "amount": product["price"],
            "currency": "KRW", "store_id": settings.PORTONE_STORE_ID, "channel_key": settings.PORTONE_CHANNEL_KEY}


class VerifyPlanPaymentReq(BaseModel):
    payment_id: str = Field(min_length=6, max_length=64)


@frontend_router.post("/billing/verify")
def frontend_verify_plan_payment(body: VerifyPlanPaymentReq, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    order = db.scalar(select(PlanOrder).where(PlanOrder.payment_id == body.payment_id, PlanOrder.user_idx == user.idx))
    if order is None:
        raise HTTPException(404, "Payment order not found")
    plan = entitlement(db, user.idx)
    if order.status == "paid":
        return {"status": "paid", "entitlement": entitlement_data(plan)}
    if not settings.PORTONE_API_SECRET:
        raise HTTPException(503, "PortOne V2 API secret is not configured on the server")
    api_request = UrlRequest(f"https://api.portone.io/payments/{body.payment_id}",
        headers={"Authorization": f"PortOne {settings.PORTONE_API_SECRET}", "Accept": "application/json"})
    try:
        with urlopen(api_request, timeout=60) as response:
            payment = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise HTTPException(502, "PortOne could not confirm this payment") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise HTTPException(502, "Could not reach PortOne to confirm payment") from exc
    received_amount = payment.get("amount")
    if isinstance(received_amount, dict):
        received_amount = received_amount.get("total")
    if (payment.get("status") != "PAID" or payment.get("paymentId") != order.payment_id
            or received_amount != order.amount or payment.get("currency") != "KRW"
            or payment.get("storeId") != settings.PORTONE_STORE_ID):
        raise HTTPException(status.HTTP_409_CONFLICT, "Payment is incomplete or does not match this order")
    now = datetime.now(timezone.utc)
    base = plan.subscription_ends_at
    if base and base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    trial = plan.trial_ends_at
    if trial and trial.tzinfo is None:
        trial = trial.replace(tzinfo=timezone.utc)
    plan.plan = "premium"
    plan.subscription_ends_at = max(value for value in (now, base, trial) if value is not None) + timedelta(days=PRODUCTS[order.plan_id]["duration_days"])
    order.status = "paid"
    db.commit()
    return {"status": "paid", "entitlement": entitlement_data(plan)}


@frontend_router.post("/rewards/ad-credit")
def frontend_reward(request: Request, db: Session = Depends(get_db)):
    result = grant_ad_credit(request, db)
    return {"credits": result["credits_granted"], "available": result["ad_credits"], "mode": "demo"}


def entitlement_data(plan: UserEntitlement) -> dict:
    now = datetime.now(timezone.utc)
    trial = plan.trial_ends_at
    subscription = plan.subscription_ends_at
    active = plan.plan == "premium" and (subscription is None or subscription > now)
    if trial and trial.tzinfo is None:
        trial = trial.replace(tzinfo=timezone.utc)
    if subscription and subscription.tzinfo is None:
        subscription = subscription.replace(tzinfo=timezone.utc)
    trial_active = bool(trial and trial > now)
    active = active or trial_active
    return {"plan": "premium" if active else "free", "trial_ends_at": trial.isoformat() if trial else None,
            "subscription_ends_at": subscription.isoformat() if subscription else None, "ad_credits": plan.ad_credits,
            "features": {"daily_lessons": True, "premium_lessons": active, "study_groups": True, "ad_credit_bonus": plan.ad_credits > 0}}


class GroupCreateReq(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)


@router.post("/groups", status_code=201)
def create_group(req: GroupCreateReq, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    group = StudyGroup(name=req.name, description=req.description, join_code=secrets.token_urlsafe(6)[:8].upper(), owner_idx=user.idx)
    db.add(group)
    db.flush()
    db.add(GroupMember(group_id=group.id, user_idx=user.idx))
    db.commit()
    return group_data(group, 1)


def group_data(group: StudyGroup, members: int) -> dict:
    return {"id": group.id, "name": group.name, "description": group.description, "join_code": group.join_code, "member_count": members, "created_at": group.created_at.isoformat()}


@router.get("/groups")
def list_groups(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    groups = db.scalars(select(StudyGroup).join(GroupMember).where(GroupMember.user_idx == user.idx).order_by(StudyGroup.created_at.desc())).all()
    return {"items": [group_data(g, db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == g.id)) or 0) for g in groups]}


class GroupJoinReq(BaseModel):
    join_code: str = Field(min_length=4, max_length=16)


@router.post("/groups/join")
def join_group(req: GroupJoinReq, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    group = db.scalar(select(StudyGroup).where(StudyGroup.join_code == req.join_code.upper()))
    if not group:
        raise HTTPException(404, "Group not found")
    member = db.scalar(select(GroupMember).where(GroupMember.group_id == group.id, GroupMember.user_idx == user.idx))
    if member is None:
        db.add(GroupMember(group_id=group.id, user_idx=user.idx))
        db.commit()
    count = db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group.id)) or 0
    return group_data(group, count)


@router.get("/plans")
def plans():
    free = {"id": "free", "name": "무료", "price": 0, "currency": "KRW", "interval": None,
            "description": "가볍게 시작하고 매일의 학습 습관을 만들어요.", "badge": None, "saving": None,
            "features": ["매일 기본 레슨", "스터디 그룹", "학습 기록"]}
    products = [{key: value for key, value in product.items() if key != "duration_days"} for product in PRODUCTS.values()]
    return {"items": [free, *products], "checkout_mode": "portone_v2"}


@router.get("/entitlement")
def get_entitlement(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    return entitlement_data(entitlement(db, user.idx))


@router.post("/trial")
def start_trial(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    plan = entitlement(db, user.idx)
    now = datetime.now(timezone.utc)
    trial = plan.trial_ends_at
    if trial and trial.tzinfo is None:
        trial = trial.replace(tzinfo=timezone.utc)
    if trial and trial > now:
        raise HTTPException(409, "Trial is already active")
    if trial:
        raise HTTPException(409, "Trial has already been used")
    plan.trial_ends_at = now + timedelta(days=7)
    db.commit()
    return {"entitlement": entitlement_data(plan)}


@router.post("/checkout")
def demo_checkout(request: Request, db: Session = Depends(get_db), plan_id: str = "premium_monthly"):
    raise HTTPException(status_code=410, detail="Demo checkout has been disabled. Use /billing/checkout.")


@router.post("/rewarded-ad")
def grant_ad_credit(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    plan = entitlement(db, user.idx)
    plan.ad_credits += 1
    db.commit()
    return {"mode": "demo", "credits_granted": 1, "ad_credits": plan.ad_credits, "message": "Demo credit granted; no ad network was contacted."}
