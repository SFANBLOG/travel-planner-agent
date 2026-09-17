"""数据库连接与会话管理（同步 SQLAlchemy 2.0）

说明：文档示例为异步(async) SQLAlchemy。为保证开箱即用（避免 aiosqlite 依赖与
事件循环复杂度），本实现采用同步会话，接口与 FastAPI 的 Depends(get_db) 一致。
生产环境可在 .env 将 DATABASE_URL 改为 postgresql+psycopg://... 直接切换。
"""
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

_url = settings.DATABASE_URL
_parsed = urlparse(_url)

if _parsed.scheme == "sqlite":
    # 自动创建 data 目录
    _db_path = Path(_parsed.path)
    if _db_path.parent != Path("") and not _db_path.is_absolute():
        _db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    if str(_db_path) not in (":memory:",):
        _db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        _url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
else:
    engine = create_engine(
        _url,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db():
    """FastAPI 依赖：提供数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表（在 lifespan 中调用）"""
    import app.models  # noqa: F401 确保模型已注册
    Base.metadata.create_all(bind=engine)


def drop_db():
    """删除所有表（慎用）"""
    import app.models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
