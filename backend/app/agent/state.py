"""Agent 状态定义"""
from typing import TypedDict, List, Optional, Dict, Any
from datetime import date
from enum import Enum


class IntentType(str, Enum):
    """旅行意图类型"""
    TRIP_PLAN = "trip_plan"          # 行程规划
    SPOT_QUERY = "spot_query"        # 景点查询
    MODIFY_TRIP = "modify_trip"      # 修改行程
    BOOKING_QUERY = "booking_query"  # 预订查询
    WEATHER_QUERY = "weather_query"  # 天气查询
    BUDGET_QUERY = "budget_query"    # 预算查询
    TIPS_QUERY = "tips_query"        # 旅行 tips
    CHITCHAT = "chitchat"            # 闲聊


class TripStatus(str, Enum):
    """行程状态"""
    PLANNING = "planning"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TravelStyle(str, Enum):
    """旅行风格"""
    RELAXED = "relaxed"          # 休闲度假
    ADVENTUROUS = "adventurous"  # 探险挑战
    CULTURAL = "cultural"        # 文化探索
    FAMILY = "family"            # 亲子游
    ROMANTIC = "romantic"        # 蜜月 / 情侣
    BUSINESS = "business"        # 商务旅行
    FOODIE = "foodie"            # 美食之旅
    PHOTOGRAPHY = "photography"  # 摄影采风


class AgentState(TypedDict, total=False):
    """Agent 状态定义（规划过程中传递的数据）"""
    user_id: str
    user_message: str

    # 意图识别
    intent: Optional[str]
    intent_confidence: float

    # 旅行需求解析
    destination: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[int]
    travelers: Optional[int]
    travel_style: Optional[str]

    # 检索结果
    retrieved_spots: List[Dict[str, Any]]
    retrieved_guides: List[Dict[str, Any]]
    weather_info: Optional[Dict[str, Any]]

    # 行程规划
    draft_itinerary: Optional[Dict[str, Any]]
    optimized_itinerary: Optional[Dict[str, Any]]

    # 预订信息
    flight_options: List[Dict[str, Any]]
    hotel_options: List[Dict[str, Any]]

    # 对话历史
    messages: List[Dict[str, str]]

    # 输出
    response: Optional[str]
    suggested_actions: List[str]

    # 错误处理
    error: Optional[str]
    retry_count: int
    used_llm: bool
