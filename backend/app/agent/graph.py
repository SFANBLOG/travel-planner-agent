"""LangGraph Agent 图构建（同步）"""
from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes import (
    parse_requirements, search_spots, fetch_weather, generate_itinerary,
    optimize_route, generate_response,
)
import logging

logger = logging.getLogger(__name__)


def _route_after_generate(state: AgentState) -> str:
    """生成节点后的条件路由：仍出错且无回复则重试（带次数上限），否则继续"""
    if state.get("error") and not state.get("response") and state.get("retry_count", 0) < 3:
        state["retry_count"] = state.get("retry_count", 0) + 1
        return "retry"
    return "proceed"


def create_travel_agent_graph():
    """创建旅行规划 Agent 图

    工作流：解析需求 → 搜索景点 → 获取天气 → 生成行程 → 优化路线 → 生成回复
    """
    graph = StateGraph(AgentState)

    graph.add_node("parse_requirements", parse_requirements)
    graph.add_node("search_spots", search_spots)
    graph.add_node("fetch_weather", fetch_weather)
    graph.add_node("generate_itinerary", generate_itinerary)
    graph.add_node("optimize_route", optimize_route)
    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("parse_requirements")
    graph.add_edge("parse_requirements", "search_spots")
    graph.add_edge("search_spots", "fetch_weather")
    graph.add_edge("fetch_weather", "generate_itinerary")
    graph.add_conditional_edges(
        "generate_itinerary",
        _route_after_generate,
        {"retry": "parse_requirements", "proceed": "optimize_route"},
    )
    graph.add_edge("optimize_route", "generate_response")
    graph.add_edge("generate_response", END)

    compiled = graph.compile()
    logger.info("✅ TravelAI Agent 图构建完成")
    return compiled


_travel_agent = None


def get_travel_agent():
    global _travel_agent
    if _travel_agent is None:
        _travel_agent = create_travel_agent_graph()
    return _travel_agent


def run_travel_agent(user_id: str, user_message: str, context: dict = None) -> dict:
    """运行旅行规划 Agent（同步）"""
    logger.info("🚀 [Agent] 开始处理用户请求: %s...", user_message[:50])
    initial: AgentState = {
        "user_id": user_id,
        "user_message": user_message,
        "intent": None,
        "intent_confidence": 0.0,
        "destination": None,
        "start_date": None,
        "end_date": None,
        "budget": None,
        "travelers": None,
        "travel_style": None,
        "retrieved_spots": [],
        "retrieved_guides": [],
        "weather_info": None,
        "draft_itinerary": None,
        "optimized_itinerary": None,
        "flight_options": [],
        "hotel_options": [],
        "messages": [],
        "response": None,
        "suggested_actions": [],
        "error": None,
        "retry_count": 0,
    }
    if context:
        for k, v in context.items():
            if k in initial:
                initial[k] = v

    agent = get_travel_agent()
    result = agent.invoke(initial)

    logger.info("✅ [Agent] 处理完成")
    return {
        "response": result.get("response"),
        "intent": result.get("intent"),
        "suggested_actions": result.get("suggested_actions", []),
        "weather_info": result.get("weather_info"),
        "draft_itinerary": result.get("draft_itinerary"),
        "optimized_itinerary": result.get("optimized_itinerary"),
        "used_llm": result.get("used_llm", False),
    }
