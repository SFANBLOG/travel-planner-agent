"""用户偏好模型"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(40), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    travel_style: Mapped[object] = mapped_column(String(50), nullable=True)
    budget_level: Mapped[object] = mapped_column(String(20), nullable=True)  # low / mid / high
    favorite_destinations: Mapped[list] = mapped_column(JSON, default=list)
    dietary: Mapped[list] = mapped_column(JSON, default=list)
    companions: Mapped[object] = mapped_column(String(50), nullable=True)  # solo / couple / family / friends
    notes: Mapped[object] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="preferences_record")
