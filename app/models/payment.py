from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ClothingOrder(Base):
    __tablename__ = "clothing_order"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_idx: Mapped[int] = mapped_column(ForeignKey("user.idx"), index=True)
    board_idx: Mapped[int] = mapped_column(ForeignKey("board.idx"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="ready")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


class PlanOrder(Base):
    __tablename__ = "plan_order"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_idx: Mapped[int] = mapped_column(ForeignKey("user.idx"), index=True)
    plan_id: Mapped[str] = mapped_column(String(40))
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="ready")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
