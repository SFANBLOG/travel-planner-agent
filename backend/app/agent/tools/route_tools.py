"""路线规划工具（最近邻 + 球面距离）"""
import math
from typing import List, Dict, Any, Optional

from app.utils.helpers import haversine, nearest_neighbor_order
import logging

logger = logging.getLogger(__name__)


class RouteOptimizer:
    """路线优化工具"""

    def optimize(self, spots: List[Dict[str, Any]], start_location: Optional[str] = None,
                 optimization_goal: str = "time") -> Dict[str, Any]:
        logger.info("🗺 优化路线，共 %d 个景点", len(spots))
        if len(spots) <= 2:
            return {
                "optimized_order": [s.get("id") for s in spots],
                "total_distance_km": 0.0,
                "estimated_time_minutes": sum(s.get("duration", 120) for s in spots),
                "segments": [],
            }

        n = len(spots)
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist[i][j] = haversine(spots[i].get("lat", 0), spots[i].get("lng", 0),
                                          spots[j].get("lat", 0), spots[j].get("lng", 0))
        order = nearest_neighbor_order(spots, lambda s: s.get("lat", 0), lambda s: s.get("lng", 0))
        total_distance = sum(dist[order[i]][order[i + 1]] for i in range(len(order) - 1))
        total_time = sum(s.get("duration", 120) for s in spots)
        travel_time = (total_distance / 30) * 60 + (len(order) - 1) * 15

        segments = []
        for i in range(len(order) - 1):
            d_km = round(dist[order[i]][order[i + 1]], 2)
            segments.append({
                "from": spots[order[i]].get("id"),
                "to": spots[order[i + 1]].get("id"),
                "distance_km": d_km,
                "estimated_time_min": int((d_km / 30) * 60 + 15),
            })
        return {
            "optimized_order": [spots[i].get("id") for i in order],
            "total_distance_km": round(total_distance, 2),
            "estimated_time_minutes": int(total_time + travel_time),
            "segments": segments,
        }


class RouteTool:
    """LangChain 风格路线工具"""

    name = "plan_route"
    description = "规划旅游路线，计算景点之间的最优顺序和交通方案。输入：景点列表（JSON）。"

    def run(self, spots_json: str) -> str:
        import json
        spots = json.loads(spots_json)
        res = RouteOptimizer().optimize(spots)
        out = "**🗺 路线规划结果：**\n\n"
        out += f"📍 途经景点：{len(res['optimized_order'])} 个\n"
        out += f"📏 总距离：{res['total_distance_km']} km\n"
        out += f"⏱ 预计时间：{res['estimated_time_minutes']} 分钟\n\n"
        for i, seg in enumerate(res.get("segments", []), 1):
            out += f"{i}. → {seg['to']}\n   📏 {seg['distance_km']} km | ⏱ {seg['estimated_time_min']} 分钟\n\n"
        return out
