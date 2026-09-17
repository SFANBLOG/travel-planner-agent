"""Schemas 聚合"""
from app.schemas.user import (
    UserRegister, UserLogin, UserUpdate, UserOut, TokenOut,
)
from app.schemas.trip import (
    TripCreate, TripOut, TripListOut, ItineraryDayOut, ItinerarySpotOut,
)
from app.schemas.spot import (
    SpotOut, SpotSearchQuery, SpotSearchResult,
)
from app.schemas.agent import (
    AgentChatRequest, AgentChatResponse, TripGenerateRequest,
)

__all__ = [
    "UserRegister", "UserLogin", "UserUpdate", "UserOut", "TokenOut",
    "TripCreate", "TripOut", "TripListOut", "ItineraryDayOut", "ItinerarySpotOut",
    "SpotOut", "SpotSearchQuery", "SpotSearchResult",
    "AgentChatRequest", "AgentChatResponse", "TripGenerateRequest",
]
