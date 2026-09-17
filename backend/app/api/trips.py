"""行程接口：列表 / 详情 / 删除 / 状态更新"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.services.trip_service import list_trips, get_trip, delete_trip, update_status
from app.schemas.trip import TripListOut
from app.agent.rule_engine import parse_requirements_rule

router = APIRouter(prefix="/trips", tags=["行程"])


def _serialize_day(day):
    return {
        "id": day.id,
        "day_number": day.day_number,
        "date": day.date.isoformat() if day.date else None,
        "theme": day.theme,
        "summary": day.summary,
        "weather_info": day.weather_info,
        "spots": [{
            "id": s.id,
            "spot_id": s.spot_id,
            "name": s.notes[:20] if s.notes else None,  # 简化展示
            "order_index": s.order_index,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "duration_minutes": s.duration_minutes,
            "transport_to_next": s.transport_to_next,
            "estimated_cost": s.estimated_cost,
            "notes": s.notes,
        } for s in day.spots],
    }


def serialize_trip(trip) -> dict:
    return {
        "id": trip.id,
        "user_id": trip.user_id,
        "title": trip.title,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat() if trip.start_date else None,
        "end_date": trip.end_date.isoformat() if trip.end_date else None,
        "budget": trip.budget,
        "status": trip.status,
        "requirements": trip.requirements,
        "generated_plan": trip.generated_plan,
        "days": [_serialize_day(d) for d in trip.days],
        "created_at": trip.created_at,
    }


@router.get("", response_model=list[TripListOut], summary="我的行程列表")
def my_trips(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trips = list_trips(db, current.id)
    return [TripListOut.model_validate(t) for t in trips]


@router.get("/{trip_id}", summary="行程详情（含每日安排）")
def trip_detail(trip_id: str, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = get_trip(db, trip_id, current.id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")
    return serialize_trip(t)


@router.delete("/{trip_id}", summary="删除行程")
def remove_trip(trip_id: str, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = delete_trip(db, trip_id, current.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")
    return {"ok": True}


@router.post("/{trip_id}/status", summary="更新行程状态（确认/取消等）")
def set_status(trip_id: str, body: dict, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_status = body.get("status")
    if not new_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少 status")
    t = update_status(db, trip_id, current.id, new_status)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")
    return serialize_trip(t)
