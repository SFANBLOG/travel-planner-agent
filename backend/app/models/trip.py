"""行程 / 日程 / 景点打卡 模型"""
import uuid
from datetime import datetime, date

from sqlalchemy import String, Integer, Date, Text, JSON, ForeignKey, DateTime, func, Time, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(40), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    budget: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="planning", index=True)
    requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_plan: Mapped[object] = mapped_column(JSON, nullable=True)  # 完整行程(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="trips")
    days: Mapped[list["ItineraryDay"]] = relationship(
        "ItineraryDay", back_populates="trip", cascade="all, delete-orphan", order_by="ItineraryDay.day_number"
    )
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=_uuid)
    trip_id: Mapped[str] = mapped_column(String(40), ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    theme: Mapped[object] = mapped_column(String(100), nullable=True)
    summary: Mapped[object] = mapped_column(Text, nullable=True)
    weather_info: Mapped[object] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    trip: Mapped["Trip"] = relationship("Trip", back_populates="days")
    spots: Mapped[list["ItinerarySpot"]] = relationship(
        "ItinerarySpot", back_populates="day", cascade="all, delete-orphan", order_by="ItinerarySpot.order_index"
    )


class ItinerarySpot(Base):
    __tablename__ = "itinerary_spots"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=_uuid)
    day_id: Mapped[str] = mapped_column(String(40), ForeignKey("itinerary_days.id", ondelete="CASCADE"), index=True)
    spot_id: Mapped[object] = mapped_column(String(40), nullable=True)  # 关联 spots.id（可为外部景点）
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[object] = mapped_column(Time, nullable=True)
    end_time: Mapped[object] = mapped_column(Time, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=120)
    transport_to_next: Mapped[object] = mapped_column(String(100), nullable=True)
    estimated_cost: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[object] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    day: Mapped["ItineraryDay"] = relationship("ItineraryDay", back_populates="spots")
