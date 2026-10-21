from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Lesson(Base):
    __tablename__ = "lesson"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    level: Mapped[str] = mapped_column(String(32), default="beginner")
    category: Mapped[str] = mapped_column(String(64), default="daily")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=5)
    is_premium: Mapped[int] = mapped_column(Integer, default=0)
    order: Mapped[int] = mapped_column(Integer, default=0)


class LessonStep(Base):
    __tablename__ = "lesson_step"
    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), index=True)
    kind: Mapped[str] = mapped_column(String(32), default="phrase")
    prompt_ko: Mapped[str] = mapped_column(Text)
    answer_en: Mapped[str] = mapped_column(Text)
    explanation_ko: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_idx: Mapped[int] = mapped_column(ForeignKey("user.idx"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), index=True)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(24), default="in_progress")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    __table_args__ = (UniqueConstraint("user_idx", "lesson_id"),)


class StudyGroup(Base):
    __tablename__ = "study_group"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    join_code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    owner_idx: Mapped[int] = mapped_column(ForeignKey("user.idx"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class GroupMember(Base):
    __tablename__ = "group_member"
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("study_group.id"), index=True)
    user_idx: Mapped[int] = mapped_column(ForeignKey("user.idx"), index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (UniqueConstraint("group_id", "user_idx"),)


class UserEntitlement(Base):
    __tablename__ = "user_entitlement"
    user_idx: Mapped[int] = mapped_column(ForeignKey("user.idx"), primary_key=True)
    plan: Mapped[str] = mapped_column(String(24), default="free")
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subscription_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ad_credits: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class LearningActivity(Base):
    __tablename__ = "learning_activity"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_idx: Mapped[int] = mapped_column(ForeignKey("user.idx"), index=True)
    activity_date: Mapped[str] = mapped_column(String(10), index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("user_idx", "activity_date"),)
