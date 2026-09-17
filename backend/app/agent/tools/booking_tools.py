"""预订查询工具（机票 / 酒店，演示用模拟数据；可接入真实供应商 API）"""
import random
from typing import Dict, Any, List, Optional

from app.config import settings
import logging

logger = logging.getLogger(__name__)


class BookingTool:
    """预订查询工具"""

    def get_flight_options(self, destination: str, budget: Optional[int] = None,
                          travelers: int = 1) -> List[Dict[str, Any]]:
        # 以出发地默认「本地」模拟；真实场景应接机票 API
        seed = sum(ord(c) for c in destination) or 1
        rng = random.Random(seed)
        base = 800 if budget is None else min(1500, budget // 4)
        options = []
        for i, airline in enumerate(["国航", "东航", "南航", "海航"]):
            price = base + rng.randint(-150, 300)
            options.append({
                "provider": airline,
                "type": "flight",
                "title": f"{airline} 往返 {destination}",
                "detail": {"cabin": "经济舱", "stops": rng.choice(["直飞", "中转1次"])},
                "price": max(300, price),
            })
        return options

    def get_hotel_options(self, destination: str, budget: Optional[int] = None,
                         travelers: int = 1) -> List[Dict[str, Any]]:
        seed = sum(ord(c) for c in destination) or 1
        rng = random.Random(seed + 7)
        base = 400 if budget is None else min(800, (budget // max(1, travelers)) // 3)
        options = []
        for brand in ["如家", "全季", "希尔顿", "万豪"]:
            price = base + rng.randint(-80, 260)
            options.append({
                "provider": brand,
                "type": "hotel",
                "title": f"{destination} {brand}（参考）",
                "detail": {"rating": round(rng.uniform(4.0, 4.9), 1), "nights": 1},
                "price": max(200, price),
            })
        return options


class BookingToolLangChain:
    name = "query_booking"
    description = "查询机票/酒店预订选项。当需要推荐交通住宿时使用。"

    def run(self, destination: str, budget: str = "") -> str:
        try:
            b = int(budget) if budget else None
        except Exception:
            b = None
        tool = BookingTool()
        flights = tool.get_flight_options(destination, b)
        hotels = tool.get_hotel_options(destination, b)
        out = f"**{destination} 预订参考：**\n\n**✈ 机票**\n"
        for f in flights:
            out += f"- {f['title']}：¥{f['price']}\n"
        out += "\n**🏨 酒店**\n"
        for h in hotels:
            out += f"- {h['title']}：¥{h['price']}/晚\n"
        return out
