"""Agent 节点定义（同步实现，LLM 缺失时降级规则引擎）

工作流：解析需求 → 搜索景点 → 获取天气 → 生成行程 → 优化路线 → 生成回复
"""
import json
import logging
from datetime import date
from typing import Dict, Any, Optional

from app.agent.state import AgentState
from app.agent.tools.spot_tools import SpotSearchTool, _STYLE_KEYWORDS
from app.agent.tools.weather_tools import WeatherTool
from app.agent.tools.route_tools import RouteOptimizer
from app.agent.rule_engine import parse_requirements_rule, build_itinerary_rule
from app.llm.client import get_llm_client
from app.utils.helpers import extract_json

logger = logging.getLogger(__name__)


def parse_requirements(state: AgentState) -> AgentState:
    """节点1：解析用户自然语言需求"""
    logger.info("📋 [Node] 解析用户旅行需求")
    llm = get_llm_client()
    msg = state.get("user_message", "")
    used_llm = False
    result: Dict[str, Any] = {}

    if llm.available:
        try:
            prompt = f"""分析用户的旅行需求，提取以下关键信息：
- destination: 目的地（城市/国家）
- start_date: 开始日期 (YYYY-MM-DD)
- end_date: 结束日期 (YYYY-MM-DD)
- budget: 预算（整数，人民币）
- travelers: 出行人数
- travel_style: 旅行风格 (relaxed/adventurous/cultural/family/romantic/business/foodie/photography)

用户输入: {msg}

返回 JSON 格式，只包含提取到的信息，未提及的字段设为 null。"""
            text = llm.complete(prompt)
            parsed = extract_json(text)
            if isinstance(parsed, dict):
                result = parsed
                used_llm = True
        except Exception as e:
            logger.warning("LLM 需求解析失败，使用规则解析: %s", e)

    if not result:
        result = parse_requirements_rule(msg)

    # 写入状态（兼容 date 对象或字符串）
    def _as_date(v):
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            from app.utils.helpers import parse_flexible_date
            return parse_flexible_date(v)
        return None

    state["destination"] = result.get("destination") or state.get("destination")
    state["start_date"] = _as_date(result.get("start_date")) or state.get("start_date")
    state["end_date"] = _as_date(result.get("end_date")) or state.get("end_date")
    state["budget"] = result.get("budget") if result.get("budget") is not None else state.get("budget")
    state["travelers"] = result.get("travelers") or state.get("travelers") or 1
    state["travel_style"] = result.get("travel_style") or state.get("travel_style") or "relaxed"
    state["used_llm"] = state.get("used_llm", False) or used_llm
    logger.info("✅ 需求解析完成: dest=%s style=%s", state.get("destination"), state.get("travel_style"))
    return state


def _style_ranked(spots: list, style: str) -> list:
    """按旅行风格 + 评分排序：风格匹配的景点优先，其次按评分降序。

    说明：默认使用哈希 embedding（语义相关性弱），因此这里在 Python 侧做
    「风格类别偏好 + 评分」排序，保证优先推荐该城市的热门必去景点。
    """
    _STYLE_CATEGORIES = {
        "foodie": {"美食街区", "商业街区"},
        "cultural": {"历史古迹", "博物馆", "宗教文化", "艺术文化"},
        "family": {"主题乐园", "自然风光", "海岛"},
        "romantic": {"自然风光", "海岛", "海滩", "休闲"},
        "photography": {"自然风光", "城市地标", "园林"},
        "adventurous": {"自然风光", "海岛", "海滩"},
        "relaxed": {"休闲", "园林", "海滩"},
        "business": {"城市地标", "商业街区"},
    }
    prefer = _STYLE_CATEGORIES.get(style, set())

    def key(s):
        cat = s.get("category") or ""
        tags = s.get("tags") or []
        hit = 0 if (cat in prefer or any(t in prefer for t in tags)) else 1
        return (hit, -(float(s.get("rating") or 0)))

    return sorted(spots, key=key)


def search_spots(state: AgentState) -> AgentState:
    """节点2：RAG 检索相关景点"""
    logger.info("🔍 [Node] 搜索景点: %s", state.get("destination"))
    if not state.get("destination"):
        logger.warning("⚠ 未指定目的地，跳过景点搜索")
        state["retrieved_spots"] = []
        return state
    try:
        style = state.get("travel_style") or "relaxed"
        kw = _STYLE_KEYWORDS.get(style, "")
        tool = SpotSearchTool()
        # 注意：不要把 travel_style 当作 category 过滤——category 的值是
        # 「历史古迹 / 美食街区」等，风格（foodie/cultural）不会命中任何记录。
        spots = tool.search(
            query=f"{state['destination']} 热门景点 必去 {kw}",
            city=state.get("destination"),
            category=None,
            top_k=20,
        )
        spots = _style_ranked(spots, style)
        # 规整为便于路线优化的字段
        norm = []
        for s in spots:
            norm.append({
                "id": s.get("id"),
                "name": s.get("name"),
                "city": s.get("city"),
                "category": s.get("category"),
                "latitude": s.get("latitude"),
                "longitude": s.get("longitude"),
                "recommend_duration": s.get("recommend_duration", 120),
                "rating": s.get("rating", 0),
                "ticket_info": s.get("ticket_info", {}),
                "address": s.get("address"),
                "description": s.get("description"),
            })
        state["retrieved_spots"] = norm
        logger.info("✅ 找到 %d 个相关景点", len(norm))
    except Exception as e:
        logger.error("❌ 景点搜索失败: %s", e)
        state["retrieved_spots"] = []
        state["error"] = str(e)
    return state


def fetch_weather(state: AgentState) -> AgentState:
    """节点3：获取天气信息（失败不阻断主流程）"""
    logger.info("🌤 [Node] 获取天气: %s", state.get("destination"))
    if not state.get("destination"):
        return state
    try:
        w = WeatherTool().get_weather(
            city=state["destination"],
            start_date=state.get("start_date"),
            end_date=state.get("end_date"),
        )
        state["weather_info"] = w
    except Exception as e:
        logger.warning("⚠ 天气获取失败: %s", e)
        state["weather_info"] = None
    return state


def generate_itinerary(state: AgentState) -> AgentState:
    """节点4：生成行程（LLM 优先，规则引擎兜底）"""
    logger.info("📝 [Node] 生成旅行行程")
    spots = state.get("retrieved_spots") or []
    if not spots:
        state["response"] = "抱歉，没有找到相关的景点信息，请尝试其他目的地或补充城市名称。"
        return state

    llm = get_llm_client()
    used_llm = False
    if llm.available:
        try:
            prompt = f"""你是一个专业的旅行规划师。根据以下信息，为用户规划最佳行程：

目的地: {state.get('destination')}
出发日期: {state.get('start_date')}
结束日期: {state.get('end_date')}
预算: {state.get('budget')} 元
人数: {state.get('travelers')} 人
旅行风格: {state.get('travel_style')}

热门景点（已按评分排序）:
{json.dumps(spots[:15], ensure_ascii=False, indent=2)}

天气:
{json.dumps(state.get('weather_info', {}), ensure_ascii=False, indent=2)}

请生成一份详细的多日行程规划（Markdown），包含每日主题、具体景点安排（含时间建议）、交通方式、餐饮建议、注意事项。
行程应考虑：景点之间距离（同一区域集中安排）、合理时间分配、用户偏好（{state.get('travel_style')} 风格）。"""
            content = llm.complete(prompt, max_tokens=3000)
            state["draft_itinerary"] = {
                "content": content,
                "days": [],
                "budget_breakdown": {},
                "spots_used": [s["id"] for s in spots[:10]],
            }
            state["response"] = content
            used_llm = True
            logger.info("✅ 行程生成成功(LLM)")
        except Exception as e:
            logger.warning("LLM 行程生成失败，使用规则引擎: %s", e)

    if not used_llm:
        try:
            plan = build_itinerary_rule(
                destination=state.get("destination"),
                start_date=state.get("start_date"),
                end_date=state.get("end_date"),
                budget=state.get("budget"),
                travelers=state.get("travelers") or 1,
                style=state.get("travel_style") or "relaxed",
                spots=spots,
            )
            state["draft_itinerary"] = plan
            state["response"] = plan["content"]
            logger.info("✅ 行程生成成功(规则引擎)")
        except Exception as e:
            logger.error("❌ 规则引擎行程生成失败: %s", e)
            state["error"] = str(e)
    state["used_llm"] = state.get("used_llm", False) or used_llm
    return state


def optimize_route(state: AgentState) -> AgentState:
    """节点5：路径优化（失败不阻断）"""
    logger.info("🗺 [Node] 优化旅行路线")
    spots = state.get("retrieved_spots") or []
    if not spots:
        return state
    try:
        daily = [{
            "id": s.get("id"),
            "lat": s.get("latitude"),
            "lng": s.get("longitude"),
            "duration": s.get("recommend_duration", 120),
        } for s in spots[:10]]
        optimized = RouteOptimizer().optimize(spots=daily, start_location=state.get("destination"))
        state["optimized_itinerary"] = optimized
        logger.info("✅ 路线优化完成")
    except Exception as e:
        logger.warning("⚠ 路线优化失败: %s", e)
    return state


def generate_response(state: AgentState) -> AgentState:
    """节点6：生成最终回复"""
    logger.info("💬 [Node] 生成最终回复")
    if state.get("error") and not state.get("response"):
        state["response"] = f"抱歉，规划过程中遇到了一些问题：{state['error']}。请稍后重试。"
        return state
    if not state.get("response"):
        state["response"] = "已经为您准备好了旅行规划，请查看！"
    state["suggested_actions"] = [
        "修改行程安排",
        "调整预算范围",
        "查看机票预订",
        "查看酒店推荐",
        "导出行程 PDF",
        "分享给好友",
    ]
    return state


def should_retry(state: AgentState) -> bool:
    """是否需要重试"""
    return bool(state.get("error")) and (state.get("retry_count", 0) < 3)


def is_trip_planning_complete(state: AgentState) -> bool:
    """行程规划是否完成"""
    return state.get("draft_itinerary") is not None and state.get("response") is not None
