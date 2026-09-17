"""应用程序配置（TravelAI 旅行智脑）

工程决策（保证开箱即用，详见 README「与文档的差异」）：
- 配置文件为 backend/.env（与 .env.example 同级）；未创建时各项使用下方默认值。
- 数据库默认 SQLite（路径 <项目根>/data/travelai.db），.env 可切 PostgreSQL。
- LLM 通过 OPENAI_API_KEY / DEEPSEEK_API_KEY / QWEN_API_KEY + BASE_URL + MODEL 配置，
  兼容 OpenAI 协议；未配置 Key 时工作流自动降级到规则引擎模式，仍可产出完整行程。
- 向量库 ChromaDB 优先，失败时降级为进程内余弦检索；embedding 默认哈希 n-gram（零依赖），
  配置远端 EMBEDDING 时才走 OpenAI 类接口。
- Redis / Celery 为可选增强：未配置时自动退化为内存缓存 + 同步生成，启动不阻塞。
"""
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

# 路径基准（app/config.py → parents[0]=app, parents[1]=backend, parents[2]=项目根）
# 注意：env_file 必须用绝对路径，否则从其它 cwd 启动时读不到 .env。
# .env 与 .env.example 同级，位于 backend/ 下（见 README 快速开始）。
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE), env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # 应用基础配置
    APP_NAME: str = "TravelAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # 数据库配置（默认落在项目根 data/，见 README「目录结构」）
    DATABASE_URL: str = f"sqlite:///{_PROJECT_ROOT / 'data' / 'travelai.db'}"

    # Redis 配置（可选；留空则使用内存缓存）
    REDIS_URL: Optional[str] = None

    # JWT 配置
    SECRET_KEY: str = "travelai-dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # 默认管理员（首次启动 / init_db 时创建）
    ADMIN_PASSWORD: str = "admin123456"

    # LLM 配置（OpenAI 兼容协议，可切换供应商）
    LLM_PROVIDER: str = "deepseek"  # openai / deepseek / qwen / none
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # 供应商独立配置（优先级低于上面的统一字段）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    QWEN_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-max"
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # RAG / 向量库配置
    EMBEDDING_MODEL: str = "hash-ngram-384"  # 默认零依赖哈希向量
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    VECTOR_STORE_TYPE: str = "chroma"  # chroma / memory
    VECTOR_STORE_PATH: str = str(_PROJECT_ROOT / "data" / "vectorstore")
    RAG_TOP_K: int = 20

    # 外部 API 配置（可选）
    AMAP_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    FLIGHT_API_KEY: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "https://*.pocketbay.app"]

    # 一次性初始化标记
    SKIP_SEED: bool = False

    @property
    def resolved_llm(self) -> dict:
        """根据 provider 解析出最终使用的 key/base/model"""
        prov = (self.LLM_PROVIDER or "none").lower()
        table = {
            "openai": (self.OPENAI_API_KEY, self.OPENAI_BASE_URL, self.OPENAI_MODEL),
            "deepseek": (self.DEEPSEEK_API_KEY, self.DEEPSEEK_BASE_URL, self.DEEPSEEK_MODEL),
            "qwen": (self.QWEN_API_KEY, self.QWEN_BASE_URL, self.QWEN_MODEL),
        }
        # 显式统一字段优先
        if self.LLM_API_KEY:
            return {
                "provider": prov if prov != "none" else "custom",
                "api_key": self.LLM_API_KEY,
                "base_url": self.LLM_BASE_URL or "https://api.openai.com/v1",
                "model": self.LLM_MODEL,
            }
        if prov in table:
            k, b, m = table[prov]
            if k:
                return {"provider": prov, "api_key": k, "base_url": b, "model": m}
        return {"provider": "none", "api_key": None, "base_url": None, "model": None}

    @property
    def llm_enabled(self) -> bool:
        return self.resolved_llm["api_key"] is not None


settings = Settings()
