"""规则引擎（离线兜底）

在未配置 LLM Key 时，由本模块完成「需求解析 → 行程编排 → 预算估算」，
保证工作流仍可产出完整、可用的行程。亦可叠加在 LLM 失败后的重试分支。
"""
import re
from datetime import date, timedelta
from typing import Dict, Any, List, Optional

from app.knowledge_base.seed_spots import CITIES
from app.utils.helpers import (haversine, parse_flexible_date, add_days, weekday_cn,
                               nearest_neighbor_order, extract_json)

# 风格 → 景点类别偏好权重（用于排序）
_STYLE_CATS = {
    "relaxed": ["休闲", "园林", "海滩", "公园", "乡村", "水乡"],
    "adventurous": ["自然风光", "自然生态", "海岛", "徒步"],
    "cultural": ["历史古迹", "博物馆", "宗教文化", "历史纪念", "艺术文化"],
    "family": ["主题乐园", "自然生态", "公园", "乡村"],
    "romantic": ["海滩", "海岛", "城市地标", "园林", "休闲"],
    "business": ["城市地标", "商业街", "休闲"],
    "foodie": ["美食街区", "商业街", "美食"],
    "photography": ["自然风光", "城市地标", "古镇", "海岛", "园林"],
}

_DINING = {
    "relaxed": "午后可在湖畔或园林茶座小憩，晚餐选本地家常菜馆。",
    "adventurous": "补充能量为主，随身带能量棒与电解质水。",
    "cultural": "晚餐可安排老字号，边吃边听历史典故。",
    "family": "选择有儿童餐与干净卫生的餐厅，避免过辣。",
    "romantic": "晚餐推荐江景/海景餐厅或特色私房菜，氛围优先。",
    "business": "商务宴请选环境安静的餐厅，注意时间安排。",
    "foodie": "每餐打卡一家必吃小店，从早点到夜宵排满美食清单。",
    "photography": "利用清晨与黄昏光线拍摄，正午转室内或休息。",
}

_TRANSPORT = {0: "步行", 1: "步行", 3: "地铁/公交", 8: "打车", 20: "打车/包车"}
_TRANSPORT_NOTE = {
    "步行": "景点相邻，步行即可。",
    "地铁/公交": "乘地铁/公交前往，约 {} 公里。",
    "打车": "建议打车或包车，约 {} 公里。",
    "打车/包车": "距离较远，建议打车或包车，约 {} 公里。",
}


def _detect_city(message: str) -> Optional[str]:
    for c in CITIES:
        if c in message:
            return c
    return None


def parse_requirements_rule(message: str) -> Dict[str, Any]:
    """从自然语言解析目的地/日期/预算/人数/风格（规则版）"""
    msg = message or ""
    res: Dict[str, Any] = {
        "destination": None, "start_date": None, "end_date": None,
        "budget": None, "travelers": 1, "travel_style": "relaxed",
    }
    # 目的地
    res["destination"] = _detect_city(msg)
    # 天数 / 日期
    m_days = re.search(r"(\d+)\s*(?:天|日|晚|夜)", msg)
    m_range = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*[~至到\-]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})", msg)
    m_single = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", msg)
    today = date.today()
    if m_range:
        d1 = parse_flexible_date(m_range.group(1))
        d2 = parse_flexible_date(m_range.group(2))
        if d1 and d2:
            res["start_date"], res["end_date"] = d1, d2
    elif m_single and m_days:
        d1 = parse_flexible_date(m_single.group(1))
        if d1:
            res["start_date"] = d1
            res["end_date"] = add_days(d1, int(m_days.group(1)) - 1)
    elif m_days:
        n = int(m_days.group(1))
        res["start_date"] = today
        res["end_date"] = add_days(today, n - 1)
    # 预算
    m_budget = re.search(r"(?:预算|大概|大约|约)?\s*(\d{3,6})\s*(?:元|块|rmb|RMB|人民币)?", msg)
    if m_budget:
        res["budget"] = int(m_budget.group(1))
    # 人数
    if "一个人" in msg or "独自" in msg or re.search(r"(\d+)\s*人", msg) is None and "独自" in msg:
        res["travelers"] = 1
    m_ppl = re.search(r"(\d+)\s*人", msg)
    if m_ppl:
        res["travelers"] = int(m_ppl.group(1))
    elif "两人" in msg or "情侣" in msg or "夫妻" in msg:
        res["travelers"] = 2
    elif "一家" in msg or "全家" in msg or "亲子" in msg:
        res["travelers"] = 3
    # 风格
    style_map = {
        "亲子": "family", "带娃": "family", "孩子": "family", "家庭": "family",
        "美食": "foodie", "吃": "foodie", "小吃": "foodie",
        "浪漫": "romantic", "情侣": "romantic", "蜜月": "romantic", "夫妻": "romantic",
        "文化": "cultural", "历史": "cultural", "博物": "cultural", "古": "cultural",
        "探险": "adventurous", "冒险": "adventurous", "徒步": "adventurous",
        "摄影": "photography", "拍照": "photography", "采风": "photography",
        "商务": "business", "出差": "business",
        "休闲": "relaxed", "度假": "relaxed", "放松": "relaxed",
    }
    for kw, st in style_map.items():
        if kw in msg:
            res["travel_style"] = st
            break
    return res


def _style_sorted(spots: List[Dict[str, Any]], style: str) -> List[Dict[str, Any]]:
    prefs = _STYLE_CATS.get(style, [])
    def key(s):
        cat = s.get("category", "")
        score = 0
        for i, p in enumerate(prefs):
            if p in cat:
                score = 100 - i
                break
        # 评分次之
        score += float(s.get("rating", 0))
        return -score
    return sorted(spots, key=key)


def _transport_for(dist_km: float) -> str:
    for thr in sorted(_TRANSPORT.keys()):
        if dist_km <= thr:
            return _TRANSPORT[thr]
    return "打车/包车"


def build_itinerary_rule(
    destination: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date],
    budget: Optional[int],
    travelers: int,
    style: str,
    spots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """构建结构化行程（规则版）"""
    today = date.today()
    if not start_date:
        start_date = today
    if not end_date or end_date < start_date:
        end_date = add_days(start_date, 2)
    n_days = max(1, (end_date - start_date).days + 1)

    # 仅保留该目的地景点；若未识别城市但传入了 spots，则全部使用
    if destination:
        city_spots = [s for s in spots if s.get("city") == destination]
    else:
        city_spots = list(spots)
    if not city_spots:
        # 无具体景点：给出通用建议
        return _generic_plan(destination, start_date, n_days, budget, travelers, style)

    ordered = _style_sorted(city_spots, style)

    days: List[Dict[str, Any]] = []
    spot_cursor = 0
    per_day = 3
    for d in range(n_days):
        day_date = add_days(start_date, d)
        day_spots = ordered[spot_cursor: spot_cursor + per_day]
        if not day_spots:
            day_spots = ordered  # 景点不足时重复利用
        spot_cursor = (spot_cursor + per_day) % max(1, len(ordered))
        # 按地理位置最近邻排序当日行程
        if len(day_spots) > 1:
            order = nearest_neighbor_order(
                day_spots,
                lambda s: s.get("latitude") or 0.0,
                lambda s: s.get("longitude") or 0.0,
            )
            day_spots = [day_spots[i] for i in order]

        start_h = 9
        day_entries = []
        prev = None
        for idx, sp in enumerate(day_spots):
            dur = int(sp.get("recommend_duration", 120))
            st = f"{start_h:02d}:00"
            et_h = start_h + dur // 60
            et_m = dur % 60
            et = f"{et_h:02d}:{et_m:02d}"
            transport = None
            note = None
            if prev and prev.get("latitude"):
                dist = haversine(prev.get("latitude"), prev.get("longitude"),
                                sp.get("latitude"), sp.get("longitude"))
                transport = _transport_for(dist)
                note = _TRANSPORT_NOTE[transport].format(round(dist, 1)) if "{}" in _TRANSPORT_NOTE[transport] else _TRANSPORT_NOTE[transport]
            day_entries.append({
                "spot_id": sp.get("id"),
                "name": sp.get("name"),
                "order_index": idx,
                "start_time": st,
                "end_time": et,
                "duration_minutes": dur,
                "transport_to_next": transport,
                "estimated_cost": int((sp.get("ticket_info") or {}).get("price", 0) or 0),
                "notes": note or sp.get("description", "")[:60],
            })
            prev = sp
            start_h = et_h + 1  # 留 1 小时间隔
        # 主题
        cats = "/".join(sorted({s.get("category", "") for s in day_spots}))
        theme = f"第{d+1}天 · {cats}" if cats else f"第{d+1}天"
        days.append({
            "day_number": d + 1,
            "date": day_date.isoformat(),
            "theme": theme,
            "summary": f"{destination} {cats}主题一日游，共 {len(day_spots)} 个景点。",
            "spots": day_entries,
            "dining": _DINING.get(style, ""),
            "tips": _day_tips(day_spots),
        })

    # 预算
    budget_breakdown = _estimate_budget(days, budget, travelers, destination)
    content = _to_markdown(destination, start_date, end_date, style, days, budget_breakdown, travelers)
    return {
        "content": content,
        "days": days,
        "budget_breakdown": budget_breakdown,
        "spots_used": [e["spot_id"] for d in days for e in d["spots"] if e.get("spot_id")],
    }


def _day_tips(spots: List[Dict[str, Any]]) -> str:
    tips = []
    for s in spots:
        oh = (s.get("opening_hours") or {})
        if oh:
            vals = list(oh.values())
            tips.append(f"{s.get('name')}：{vals[0]}")
        ti = (s.get("ticket_info") or {})
        if ti.get("price"):
            tips.append(f"{s.get('name')} 门票约 ¥{ti['price']}")
    return "；".join(tips[:3])


def _estimate_budget(days, budget, travelers, destination) -> Dict[str, Any]:
    ticket = sum(e["estimated_cost"] for d in days for e in d["spots"]) * travelers
    food_per_day = 150 * travelers
    food = food_per_day * len(days)
    hotel_per_night = 400
    hotel = hotel_per_night * max(1, len(days) - 1)
    transport_local = 60 * len(days) * travelers
    total = ticket + food + hotel + transport_local
    return {
        "ticket": ticket, "food": food, "hotel": hotel,
        "transport": transport_local, "total": total,
        "per_person": total // max(1, travelers),
        "user_budget": budget,
        "within_budget": (budget is None) or (total <= budget),
    }


def _to_markdown(destination, start_date, end_date, style, days, bb, travelers) -> str:
    lines = [f"# {destination or '目的地'} {len(days)} 天行程规划（{style} 风格 · {travelers} 人）",
             f"**日期**：{start_date} ~ {end_date}", ""]
    for d in days:
        lines.append(f"## 第{d['day_number']}天（{d['date']} {weekday_cn(d['date'] if isinstance(d['date'], date) else date.fromisoformat(d['date']))}）{d['theme']}")
        for e in d["spots"]:
            t = f"{e['start_time']}-{e['end_time']}"
            tr = f" → {e['transport_to_next']}" if e["transport_to_next"] else ""
            cost = f" ¥{e['estimated_cost']}" if e["estimated_cost"] else " 免费"
            lines.append(f"- **{t}** {e['name']}{cost}{tr}")
            if e["notes"]:
                lines.append(f"  - {e['notes']}")
        if d.get("dining"):
            lines.append(f"- 🍜 餐饮：{d['dining']}")
        if d.get("tips"):
            lines.append(f"- 💡 提示：{d['tips']}")
        lines.append("")
    lines.append("## 预算估算")
    lines.append(f"- 门票：¥{bb['ticket']}　餐饮：¥{bb['food']}　住宿：¥{bb['hotel']}　市内交通：¥{bb['transport']}")
    lines.append(f"- **合计约 ¥{bb['total']}**（人均 ¥{bb['per_person']}）")
    if bb["user_budget"]:
        flag = "✅ 在预算内" if bb["within_budget"] else "⚠️ 超出预算，建议压缩住宿或景点"
        lines.append(f"- 你的预算 ¥{bb['user_budget']}：{flag}")
    return "\n".join(lines)


def _generic_plan(destination, start_date, n_days, budget, travelers, style) -> Dict[str, Any]:
    days = []
    for d in range(n_days):
        day_date = add_days(start_date, d)
        days.append({
            "day_number": d + 1,
            "date": day_date.isoformat(),
            "theme": f"第{d+1}天 · 自由探索",
            "summary": f"未在知识库中找到「{destination}」的具体景点，建议围绕市中心地标与美食街区自由安排。",
            "spots": [],
            "dining": "推荐前往当地人气美食街区，体验地道风味。",
            "tips": "可在平台补充该城市的景点数据后重新生成更精准的行程。",
        })
    bb = {"ticket": 0, "food": 150 * travelers * n_days, "hotel": 400 * max(1, n_days - 1),
          "transport": 60 * n_days * travelers, "total": 0, "per_person": 0,
          "user_budget": budget, "within_budget": True}
    bb["total"] = bb["food"] + bb["hotel"] + bb["transport"]
    bb["per_person"] = bb["total"] // max(1, travelers)
    content = f"# {destination or '目的地'} {n_days} 天行程（通用模板）\n\n" + \
              "暂未收录该目的地详细景点，已生成通用框架，建议补充数据后重新规划。\n"
    return {"content": content, "days": days, "budget_breakdown": bb, "spots_used": []}
