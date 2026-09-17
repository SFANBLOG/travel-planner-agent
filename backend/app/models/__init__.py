"""模型聚合导入，确保 Base.metadata 注册所有表"""
from app.models.user import User
from app.models.trip import Trip, ItineraryDay, ItinerarySpot
from app.models.spot import Spot
from app.models.booking import Booking
from app.models.preference import UserPreference

__all__ = [
    "User",
    "Trip",
    "ItineraryDay",
    "ItinerarySpot",
    "Spot",
    "Booking",
    "UserPreference",
]
