"""RAG 知识库 Chain

封装景点库（travel_spots）与攻略库（travel_guides）两类向量检索。
默认使用哈希 embedding + Chroma/内存向量库，无需任何远端服务即可工作。

注意：Chroma 的 metadata 不支持嵌套 dict，写入前会由 _dump_meta_value 序列化。
"""
import json
from typing import List, Dict, Any, Optional

from app.rag.vectorstore import get_vector_store


def _dump_meta_value(v: Any) -> Any:
    """Chroma 元数据只支持 str/int/float/bool/list/None，嵌套结构需序列化。"""
    if isinstance(v, (dict,)):
        return json.dumps(v, ensure_ascii=False)
    return v


def _load_dict(v: Any) -> dict:
    """把可能已序列化的元数据还原为 dict。"""
    if isinstance(v, dict):
        return v
    if isinstance(v, str) and v.strip():
        try:
            d = json.loads(v)
            return d if isinstance(d, dict) else {}
        except Exception:
            return {}
    return {}


class RAGChain:
    """RAG 知识库 Chain"""

    def __init__(self):
        self.spot_store = get_vector_store("travel_spots")
        self.guide_store = get_vector_store("travel_guides")

    # ---------- 写入 ----------
    def add_spots(self, spots: List[Dict[str, Any]]) -> int:
        if not spots:
            return 0
        docs, metas, ids = [], [], []
        for sp in spots:
            meta = {k: _dump_meta_value(v) for k, v in {
                "id": sp.get("id"),
                "name": sp.get("name"),
                "name_en": sp.get("name_en"),
                "city": sp.get("city"),
                "country": sp.get("country", "中国"),
                "category": sp.get("category"),
                "address": sp.get("address"),
                "latitude": sp.get("latitude"),
                "longitude": sp.get("longitude"),
                "rating": sp.get("rating", 0),
                "ticket_info": sp.get("ticket_info", {}),
                "recommend_duration": sp.get("recommend_duration", 120),
                "tags": sp.get("tags", []),
                "type": "spot",
            }.items()}
            content = f"{sp.get('name','')} {sp.get('city','')} {sp.get('category','')} " \
                      f"{sp.get('address','')} {sp.get('description','')}"
            docs.append(content)
            metas.append(meta)
            ids.append(str(sp.get("id")))
        self.spot_store.add_texts(docs, metas, ids)
        return len(docs)

    def add_guides(self, guides: List[Dict[str, Any]]) -> int:
        if not guides:
            return 0
        docs, metas, ids = [], [], []
        for g in guides:
            meta = {
                "id": g.get("id"),
                "title": g.get("title"),
                "source": g.get("source"),
                "url": g.get("url"),
                "type": "guide",
            }
            docs.append(g.get("content", ""))
            metas.append(meta)
            ids.append(str(g.get("id")))
        self.guide_store.add_texts(docs, metas, ids)
        return len(docs)

    # ---------- 检索 ----------
    def search_spots(self, query: str, top_k: int = 10,
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = self.spot_store.similarity_search_with_score(
            query=query, k=top_k,
            filter={k: v for k, v in (filters or {}).items() if v is not None},
        )
        spots = []
        for doc, score in results:
            m = doc.metadata
            spots.append({
                "id": m.get("id"),
                "name": m.get("name"),
                "name_en": m.get("name_en"),
                "city": m.get("city"),
                "country": m.get("country"),
                "category": m.get("category"),
                "address": m.get("address"),
                "latitude": m.get("latitude"),
                "longitude": m.get("longitude"),
                "rating": m.get("rating", 0),
                "ticket_info": _load_dict(m.get("ticket_info")) or {},
                "description": (doc.page_content or "")[:500],
                "recommend_duration": m.get("recommend_duration", 120),
                "tags": m.get("tags", []),
                "relevance_score": round(1 - score, 4),
            })
        spots.sort(key=lambda x: x["relevance_score"], reverse=True)
        return spots

    def search_guides(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.guide_store.similarity_search(query=query, k=top_k)
        return [{
            "id": d.metadata.get("id"),
            "title": d.metadata.get("title"),
            "source": d.metadata.get("source"),
            "content": d.page_content,
            "url": d.metadata.get("url"),
        } for d in results]

    def generate_context(self, destination: str, travel_style: str, duration: int) -> str:
        spots = self.search_spots(query=f"{destination} {travel_style} 热门", top_k=10)
        guides = self.search_guides(query=f"{destination} 攻略 tips", top_k=3)
        context = f"**{destination} 旅行信息汇总**\n\n"
        if spots:
            context += "### 🏛 热门景点\n"
            for s in spots[:5]:
                context += f"- {s['name']}（评分：{s['rating']}）\n"
            context += "\n"
        if guides:
            context += "### 📖 旅行攻略\n"
            for g in guides[:3]:
                context += f"- {g['title']}\n"
        return context
