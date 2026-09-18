"""TravelAI 旅行智脑 —— FastAPI 入口

启动流程（lifespan）：
1. 建表；2. 创建默认 admin；3. 注入知识库（景点 + 攻略）到 DB 与向量库。
知识库注入失败不阻塞启动。
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# 允许直接运行本文件（IDE 的 Run 按钮 / `python app/main.py`）：
# 将 backend/ 注入 sys.path，使 `from app.xxx` 这类绝对导入可用。
# 否则 Python 只会把脚本所在目录 backend/app 加入 sys.path，导致
# ModuleNotFoundError: No module named 'app'。
# 推荐启动方式仍是从 backend/ 目录执行：uvicorn app.main:app --reload --port 8000
_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db, SessionLocal
from app.models.user import User
from app.core.security import hash_password
from app.knowledge_base.seed import seed_all
from app.api import api_router
import logging

logger = logging.getLogger("travelai")

_FRONTEND_DIST = str(Path(__file__).resolve().parents[2] / "frontend" / "dist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    init_db()
    logger.info("数据库表已就绪")
    # 默认管理员
    _ensure_admin()
    # 知识库注入（失败不阻塞；SKIP_SEED=true 时跳过）
    if settings.SKIP_SEED:
        logger.info("SKIP_SEED=true，跳过知识库注入")
    else:
        try:
            db = SessionLocal()
            try:
                seed_all(db)
            finally:
                db.close()
        except Exception as e:
            logger.warning("知识库初始化异常: %s", e)
    yield


def _ensure_admin():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@travelai.com",
                password_hash=hash_password(settings.ADMIN_PASSWORD),
            )
            db.add(admin)
            db.commit()
            logger.info("已创建默认管理员 admin")
    finally:
        db.close()


app = FastAPI(
    title="TravelAI 旅行智脑",
    version=settings.APP_VERSION,
    description="基于 LLM · Agent · RAG · LangGraph 的智能旅行规划平台",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["系统"])
def health():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_configured": settings.llm_enabled,
        "embedding_provider": "hash-ngram",
        "vector_store_type": settings.VECTOR_STORE_TYPE,
        "knowledge_backend": "rag",
    }


@app.get("/api/health", tags=["系统"])
def api_health():
    return health()


@app.websocket("/api/ws/progress")
async def ws_progress(websocket: WebSocket):
    """轻量级实时通道：前端可连接以接收规划进度通知（演示用）"""
    await websocket.accept()
    try:
        await websocket.send_json({"type": "connected", "message": "TravelAI 实时通道已连接"})
        while True:
            # 简单保活；真实场景可由后台任务推送生成进度
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        pass


# ---- 前端 SPA 静态资源（生产/部署时由后端托管 dist）----
if os.path.isdir(_FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def spa_index(full_path: str):
        index = os.path.join(_FRONTEND_DIST, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)
        return {"detail": "前端未构建，请先 npm run build"}
else:
    @app.get("/")
    def root():
        return {"message": "TravelAI API 运行中，前端未构建。访问 /docs 查看接口。"}


# ---- 直接运行入口（IDE Run / `python app/main.py`）----
if __name__ == "__main__":
    import uvicorn

    # 端口与 README、前端 vite 代理（127.0.0.1:8000）保持一致，可用环境变量覆盖
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
