"""景点搜索工具（基于 RAG 知识库）"""
from typing import List, Dict, Any, Optional

from app.rag.chain import RAGChain
import logging

logger = logging.getLogger(__name__)

_STYLE_KEYWORDS = {
    "relaxed": "休闲 放松 舒适",
    "adventurous": "刺激 冒险 挑战",
    "cultural": "历史 文化 博物馆",
    "family": "亲子 儿童 家庭",
    "romantic": "浪漫 情侣 约会",
    "business": "商务 效率 便捷",
    "foodie": "美食 餐厅 小吃",
    "photography": "风景 拍照 美景",
}


class SpotSearchTool:
    """景点搜索工具"""

    def __init__(self):
        self.rag = RAGChain()

    def search(self, query: str, city: Optional[str] = None,
               category: Optional[str] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        search_query = f"{city} {query}" if city else query
        flt = {k: v for k, v in {"city": city, "category": category}.items() if v}
        return self.rag.search_spots(query=search_query, top_k=top_k, filters=flt or None)

    def get_spot_detail(self, spot_id: str) -> Optional[Dict[str, Any]]:
        from app.services.spot_service import SpotService
        try:
            return SpotService().get_spot_by_id(spot_id)
        except Exception:
            return None

    def get_recommendations(self, city: str, style: str = "relaxed", limit: int = 10) -> List[Dict[str, Any]]:
        keywords = _STYLE_KEYWORDS.get(style, "")
        query = f"{city} {keywords} 必去"
        return self.search(query, city=city, top_k=limit)


class SpotTool:
    """LangChain 风格景点工具（保持与文档一致的接口）"""

    name = "search_spots"
    description = "搜索热门景点信息。当用户输入某地景点、必去地方、推荐游览地时使用。"

    def run(self, city: str, preference: str = "") -> str:
        tool = SpotSearchTool()
        spots = tool.get_recommendations(city=city, style=preference or "relaxed", limit=10)
        if not spots:
            return f"抱歉，没有找到 {city} 相关的景点信息。"
        result = f"**{city} 热门景点推荐：**\n\n"
        for i, s in enumerate(spots, 1):
            result += f"{i}. **{s['name']}**\n"
            result += f"   📍 {s.get('address', '地址未知')}\n"
            result += f"   ⭐ 评分：{s.get('rating', 'N/A')}\n"
            result += f"   ⏱ 建议游览：{s.get('recommend_duration', 120)} 分钟\n"
            result += f"   💰 门票：{s.get('ticket_info', {}).get('price', '免费')}\n\n"
        return result
