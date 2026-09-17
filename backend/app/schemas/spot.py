"""景点相关 Pydantic 模型"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class SpotOut(BaseModel):
    id: str
    name: str
    name_en: Optional[str] = None
    city: str
    country: str = "中国"
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = None
    ticket_info: dict = {}
    rating: float = 0.0
    review_count: int = 0
    recommend_duration: int = 120
    tags: List[str] = []
    images: List[str] = []
    opening_hours: dict = {}
    best_season: List[str] = []

    model_config = {"from_attributes": True}


class SpotSearchQuery(BaseModel):
    query: Optional[str] = ""
    city: Optional[str] = None
    category: Optional[str] = None
    style: Optional[str] = None
    top_k: int = 10


class SpotSearchResult(BaseModel):
    id: str
    name: str
    city: str
    category: str
    rating: float = 0.0
    address: Optional[str] = None
    recommend_duration: int = 120
    ticket_info: dict = {}
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tags: List[str] = []
    relevance_score: float = 0.0
