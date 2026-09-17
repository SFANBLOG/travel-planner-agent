"""景点服务：数据库查询 + RAG 检索"""
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models.spot import Spot
from app.rag.chain import RAGChain


class SpotService:
    def __init__(self):
        self.rag = RAGChain()

    def get_spot_by_id(self, spot_id: str) -> Optional[Dict[str, Any]]:
        # 先在 RAG metadata 中找（含向量库内的全部景点）
        found = self.rag.search_spots(query=spot_id, top_k=1, filters={"id": spot_id})
        if found:
            return found[0]
        return None

    def search(self, query: str = "", city: Optional[str] = None,
               category: Optional[str] = None, style: Optional[str] = None,
               top_k: int = 10) -> List[Dict[str, Any]]:
        flt = {k: v for k, v in {"city": city, "category": category}.items() if v}
        q = query or (f"{city or ''} {style or ''} 热门")
        return self.rag.search_spots(query=q, top_k=top_k, filters=flt or None)

    def list_by_city(self, city: str, db: Session) -> List[Spot]:
        return db.query(Spot).filter(Spot.city == city).order_by(Spot.rating.desc()).all()
