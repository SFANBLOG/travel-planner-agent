"""行程服务：创建/查询/持久化 Agent 生成的行程"""
import uuid
from datetime import date, datetime, time
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.models.trip import Trip, ItineraryDay, ItinerarySpot
from app.models.user import User


def _to_time(s: Optional[str]) -> Optional[time]:
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%H:%M").time()
    except Exception:
        return None


def _to_date(s: Any) -> date:
    if isinstance(s, date) and not isinstance(s, datetime):
        return s
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, str):
        from app.utils.helpers import parse_flexible_date
        return parse_flexible_date(s) or date.today()
    return date.today()


def create_trip_from_agent(
    db: Session,
    user: User,
    title: str,
    destination: str,
    start_date: Any,
    end_date: Any,
    budget: int,
    agent_result: Dict[str, Any],
    travel_style: str = "relaxed",
    travelers: int = 1,
    requirements: dict = None,
) -> Trip:
    """根据 Agent 结果落库：Trip + ItineraryDay + ItinerarySpot"""
    sd = _to_date(start_date)
    ed = _to_date(end_date)
    draft = agent_result.get("draft_itinerary") or {}
    plan = {
        "content": agent_result.get("response"),
        "days": draft.get("days", []),
        "budget_breakdown": draft.get("budget_breakdown", {}),
        "spots_used": draft.get("spots_used", []),
        "weather_info": agent_result.get("weather_info"),
        "optimized_itinerary": agent_result.get("optimized_itinerary"),
        "used_llm": agent_result.get("used_llm", False),
    }

    trip = Trip(
        id=uuid.uuid4().hex,
        user_id=user.id,
        title=title or f"{destination} { (ed - sd).days + 1 } 天行程",
        destination=destination,
        start_date=sd,
        end_date=ed,
        budget=budget or 0,
        status="planning",
        requirements=requirements or {},
        generated_plan=plan,
    )
    db.add(trip)
    db.flush()

    # 落库每日行程（rule engine 才有结构化 days；LLM 仅 markdown 时 days 为空）
    for d in draft.get("days", []):
        day = ItineraryDay(
            id=uuid.uuid4().hex,
            trip_id=trip.id,
            day_number=d.get("day_number", 1),
            date=_to_date(d.get("date")),
            theme=d.get("theme"),
            summary=d.get("summary"),
            weather_info=agent_result.get("weather_info"),
        )
        db.add(day)
        db.flush()
        for e in d.get("spots", []):
            ispot = ItinerarySpot(
                id=uuid.uuid4().hex,
                day_id=day.id,
                spot_id=e.get("spot_id"),
                order_index=e.get("order_index", 0),
                start_time=_to_time(e.get("start_time")),
                end_time=_to_time(e.get("end_time")),
                duration_minutes=e.get("duration_minutes", 120),
                transport_to_next=e.get("transport_to_next"),
                estimated_cost=e.get("estimated_cost", 0),
                notes=e.get("notes"),
            )
            db.add(ispot)
    db.commit()
    db.refresh(trip)
    return trip


def get_trip(db: Session, trip_id: str, user_id: str) -> Optional[Trip]:
    return db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()


def list_trips(db: Session, user_id: str) -> List[Trip]:
    return db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.created_at.desc()).all()


def delete_trip(db: Session, trip_id: str, user_id: str) -> bool:
    t = get_trip(db, trip_id, user_id)
    if not t:
        return False
    db.delete(t)
    db.commit()
    return True


def update_status(db: Session, trip_id: str, user_id: str, status: str) -> Optional[Trip]:
    t = get_trip(db, trip_id, user_id)
    if not t:
        return None
    t.status = status
    db.commit()
    db.refresh(t)
    return t
