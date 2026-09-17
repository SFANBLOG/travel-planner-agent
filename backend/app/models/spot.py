"""景点库（SPOT）模型 —— 知识库检索与展示的基础数据"""
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, Text, JSON, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class Spot(Base):
    __tablename__ = "spots"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[object] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="中国")
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    latitude: Mapped[object] = mapped_column(Float, nullable=True)
    longitude: Mapped[object] = mapped_column(Float, nullable=True)
    address: Mapped[object] = mapped_column(Text, nullable=True)
    description: Mapped[object] = mapped_column(Text, nullable=True)
    ticket_info: Mapped[dict] = mapped_column(JSON, default=dict)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    recommend_duration: Mapped[int] = mapped_column(Integer, default=120)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    images: Mapped[list] = mapped_column(JSON, default=list)
    opening_hours: Mapped[dict] = mapped_column(JSON, default=dict)
    best_season: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# 文档 DDL 中还包含基于 pgvector 的 ivfflat 索引，SQLite 不支持向量索引，
# 这里仅保留常规 B-Tree 索引以保证可移植性。
Index("idx_spots_rating", Spot.rating.desc())
