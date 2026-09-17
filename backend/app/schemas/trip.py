"""行程相关 Pydantic 模型

注意：字段名 date/time 会遮蔽 datetime 的同名类型，导致注解被解析成
Optional[None]。这里用 _Date / _Time 别名规避。
"""
from datetime import datetime, date as _Date, time as _Time
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    start_date: _Date
    end_date: _Date
    budget: int = 0
    # 自然语言需求（可空，由 Agent 解析）
    user_message: Optional[str] = None
    travel_style: Optional[str] = "relaxed"
    travelers: int = 1
    preferences: dict = {}


class ItinerarySpotOut(BaseModel):
    id: Optional[str] = None
    spot_id: Optional[str] = None
    name: Optional[str] = None
    order_index: int = 0
    start_time: Optional[_Time] = None
    end_time: Optional[_Time] = None
    duration_minutes: int = 120
    transport_to_next: Optional[str] = None
    estimated_cost: int = 0
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ItineraryDayOut(BaseModel):
    id: Optional[str] = None
    day_number: int = 0
    date: Optional[_Date] = None
    theme: Optional[str] = None
    summary: Optional[str] = None
    weather_info: Optional[dict] = None
    spots: List[ItinerarySpotOut] = []

    model_config = {"from_attributes": True}


class TripOut(BaseModel):
    id: str
    user_id: str
    title: str
    destination: str
    start_date: Optional[_Date] = None
    end_date: Optional[_Date] = None
    budget: int = 0
    status: str = "planning"
    requirements: dict = {}
    generated_plan: Optional[dict] = None
    days: List[ItineraryDayOut] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TripListOut(BaseModel):
    id: str
    title: str
    destination: str
    start_date: Optional[_Date] = None
    end_date: Optional[_Date] = None
    budget: int = 0
    status: str = "planning"
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
