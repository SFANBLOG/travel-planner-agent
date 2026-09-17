"""知识库初始化：景点库落库 + 向量库注入（幂等）"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.spot import Spot
from app.knowledge_base.seed_spots import SPOTS
from app.knowledge_base.seed_guides import GUIDES
from app.rag.chain import RAGChain
import logging

logger = logging.getLogger(__name__)


def seed_spots_to_db(db: Session):
    """将种子景点写入 spots 表（仅在为空时）"""
    cnt = db.query(func.count(Spot.id)).scalar() or 0
    if cnt > 0:
        logger.info("spots 表已有 %d 条，跳过种子注入", cnt)
        return 0
    added = 0
    for s in SPOTS:
        spot = Spot(
            id=str(s.get("id")),
            name=s["name"],
            name_en=s.get("name_en"),
            city=s["city"],
            country=s.get("country", "中国"),
            category=s["category"],
            latitude=s.get("latitude"),
            longitude=s.get("longitude"),
            address=s.get("address"),
            description=s.get("description"),
            ticket_info=s.get("ticket_info", {}),
            rating=float(s.get("rating", 0)),
            review_count=int(s.get("review_count", 0)),
            recommend_duration=int(s.get("recommend_duration", 120)),
            tags=s.get("tags", []),
            images=s.get("images", []),
            opening_hours=s.get("opening_hours", {}),
            best_season=s.get("best_season", []),
        )
        db.add(spot)
        added += 1
    db.commit()
    logger.info("已向 spots 表写入 %d 条景点", added)
    return added


def seed_rag():
    """向向量库注入景点 + 攻略（幂等）"""
    rag = RAGChain()
    if rag.spot_store.count() == 0:
        n = rag.add_spots(SPOTS)
        logger.info("向量库注入 %d 个景点", n)
    else:
        logger.info("向量库景点已存在，跳过")
    if rag.guide_store.count() == 0:
        n = rag.add_guides(GUIDES)
        logger.info("向量库注入 %d 篇攻略", n)


def seed_all(db: Session):
    seed_spots_to_db(db)
    try:
        seed_rag()
    except Exception:
        # 用 exception 记录完整堆栈，避免向量库空了却只看到一行警告
        logger.exception("RAG 向量库注入失败（不影响主流程）")
