"""景点接口：搜索 / 详情 / 按城市列出"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.spot_service import SpotService
from app.schemas.spot import SpotSearchResult, SpotOut
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/spots", tags=["景点"])


@router.get("/search", response_model=list[SpotSearchResult], summary="RAG 检索景点")
def search_spots(
    q: str = Query("", description="查询关键词"),
    city: str = Query(None),
    category: str = Query(None),
    style: str = Query(None),
    top_k: int = Query(10, ge=1, le=50),
    _: User = Depends(get_current_user),
):
    results = SpotService().search(query=q, city=city, category=category, style=style, top_k=top_k)
    return [SpotSearchResult(**r) for r in results]


@router.get("/{spot_id}", response_model=SpotOut, summary="景点详情")
def spot_detail(spot_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    sp = SpotService().get_spot_by_id(spot_id)
    if not sp:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="景点不存在")
    return SpotOut(**sp)
