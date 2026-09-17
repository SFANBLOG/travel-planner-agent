"""预订信息（机票 / 酒店 / 门票等）模型"""
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, Text, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=_uuid)
    trip_id: Mapped[str] = mapped_column(String(40), ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # flight / hotel / ticket / other
    provider: Mapped[object] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    trip: Mapped["Trip"] = relationship("Trip", back_populates="bookings")
