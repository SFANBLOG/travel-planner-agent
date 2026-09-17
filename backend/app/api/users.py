"""用户资料与偏好接口"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.preference import UserPreference
from app.schemas.user import UserOut, UserUpdate
from app.core.deps import get_current_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.put("/me", response_model=UserOut, summary="更新当前用户资料")
def update_me(
    payload: UserUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.avatar_url is not None:
        current.avatar_url = payload.avatar_url
    if payload.preferences is not None:
        current.preferences = payload.preferences
    db.commit()
    db.refresh(current)
    return UserOut.model_validate(current)


@router.get("/preferences", summary="获取偏好")
def get_preferences(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current.id).first()
    if not pref:
        return {}
    return {
        "travel_style": pref.travel_style,
        "budget_level": pref.budget_level,
        "favorite_destinations": pref.favorite_destinations,
        "dietary": pref.dietary,
        "companions": pref.companions,
        "notes": pref.notes,
    }


@router.put("/preferences", summary="保存偏好")
def save_preferences(body: dict, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current.id).first()
    if not pref:
        pref = UserPreference(user_id=current.id)
        db.add(pref)
    for k in ("travel_style", "budget_level", "favorite_destinations", "dietary", "companions", "notes"):
        if k in body:
            setattr(pref, k, body[k])
    db.commit()
    return {"ok": True}
