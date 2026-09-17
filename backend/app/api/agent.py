"""Agent 交互接口：自然语言对话 + 一键行程生成"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.agent import AgentChatRequest, AgentChatResponse, TripGenerateRequest
from app.core.deps import get_current_user
from app.models.user import User
from app.agent.graph import run_travel_agent
from app.services.trip_service import create_trip_from_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat", response_model=AgentChatResponse, summary="与旅行 Agent 对话")
def agent_chat(
    payload: AgentChatRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """运行 LangGraph 多智能体工作流，返回行程建议等"""
    result = run_travel_agent(
        user_id=current.id,
        user_message=payload.message,
        context={"user_id": current.id, **(payload.context or {})},
    )
    return AgentChatResponse(**result)


@router.post("/generate-trip", summary="一键生成行程并落库")
def generate_trip(
    payload: TripGenerateRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """解析需求 → 规划 → 落库，返回新建行程"""
    message = payload.user_message
    result = run_travel_agent(user_id=current.id, user_message=message)
    # 从 Agent 解析出的需求（state 未直接返回，这里用规则再解析一次以保证落库字段完整）
    from app.agent.rule_engine import parse_requirements_rule
    from app.utils.helpers import parse_flexible_date
    from datetime import date, datetime

    def _pdate(v):
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            return parse_flexible_date(v)
        return None

    req = parse_requirements_rule(message)
    destination = payload.destination or req.get("destination") or "未知目的地"
    sd = _pdate(payload.start_date) or _pdate(req.get("start_date"))
    ed = _pdate(payload.end_date) or _pdate(req.get("end_date"))
    budget = payload.budget if payload.budget is not None else (req.get("budget") or 0)
    style = payload.travel_style or req.get("travel_style") or "relaxed"
    travelers = payload.travelers or req.get("travelers") or 1
    day_count = (ed - sd).days + 1 if sd and ed else 3
    title = payload.title or f"{destination} {day_count} 天行程"

    trip = create_trip_from_agent(
        db=db,
        user=current,
        title=title,
        destination=destination,
        start_date=sd,
        end_date=ed,
        budget=budget,
        agent_result=result,
        travel_style=style,
        travelers=travelers,
        requirements={"style": style, "travelers": travelers, "message": message},
    )
    from app.schemas.trip import TripOut
    return TripOut.model_validate(trip)
