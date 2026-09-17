"""用户模型"""
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[object] = mapped_column(String(500), nullable=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_level: Mapped[str] = mapped_column(String(20), default="moderate")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    preferences_record: Mapped[object] = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
