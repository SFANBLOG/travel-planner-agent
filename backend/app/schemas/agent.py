"""Agent 交互相关 Pydantic 模型"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    # 可选上下文（已存在行程等）
    trip_id: Optional[str] = None
    context: dict = {}


class AgentChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    suggested_actions: List[str] = []
    weather_info: Optional[dict] = None
    draft_itinerary: Optional[dict] = None
    optimized_itinerary: Optional[dict] = None
    used_llm: bool = False


class TripGenerateRequest(BaseModel):
    """触发一次完整行程规划（走 LangGraph 工作流）"""
    user_message: str = Field(..., min_length=1)
    destination: Optional[str] = None
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None
    budget: Optional[int] = None
    travelers: int = 1
    travel_style: Optional[str] = "relaxed"
    title: Optional[str] = None
