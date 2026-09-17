# TravelAI 旅行智脑 —— 智能旅行规划 Agent

> 基于 **FastAPI + LangGraph + RAG + Vue 3** 的多智能体旅行规划平台。
> 用户用自然语言描述出行需求，Agent 自动完成「需求解析 → 景点检索 → 天气获取 → 行程生成 → 路线优化 → 结果成文」全链路，并支持一键落库为「我的行程」。

---

## 一、项目亮点

| 能力 | 实现方式 |
| --- | --- |
| 多智能体编排 | LangGraph `StateGraph` 六节点流水线，带条件路由与失败重试 |
| RAG 知识库 | 景点 / 攻略双库检索，ChromaDB 持久化，默认零依赖哈希 n-gram 向量 |
| LLM 供应商可切换 | OpenAI 兼容协议，支持 DeepSeek / OpenAI / 通义千问（Qwen） |
| 优雅降级 | 未配置 LLM Key 时自动回落规则引擎，仍可产出完整行程；向量库不可用时回落进程内余弦检索 |
| 前后端分离 | Vue 3 + TypeScript + Vite + Element Plus + Pinia，后端 FastAPI 托管构建产物 |
| 实时通道 | WebSocket `/api/ws/progress` 推送规划进度 |
| 认证鉴权 | JWT + bcrypt，受保护路由由前端路由守卫 + 后端依赖注入双重校验 |

---

## 二、技术栈

**后端**

- FastAPI · Uvicorn · Pydantic v2 / pydantic-settings
- SQLAlchemy 2.0（默认 SQLite，可切 PostgreSQL）
- LangGraph · LangChain-OpenAI · ChromaDB
- python-jose（JWT）· bcrypt（口令哈希）

**前端**

- Vue 3 · TypeScript · Vite 6
- Element Plus · Pinia · Vue Router · Axios

---

## 三、目录结构

```
travel-planner-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口（lifespan：建表 / 建管理员 / 注入知识库）
│   │   ├── config.py               # 全局配置（LLM 解析、向量库、CORS）
│   │   ├── database.py             # 引擎与会话
│   │   ├── agent/                  # LangGraph 智能体
│   │   │   ├── graph.py            #   图构建与运行入口
│   │   │   ├── nodes.py            #   六个节点实现
│   │   │   ├── state.py            #   AgentState 定义
│   │   │   ├── rule_engine.py      #   规则引擎（LLM 降级路径 / 字段兜底）
│   │   │   └── tools/              #   工具集：spot / route / weather / booking / memory
│   │   ├── api/                    # 路由：auth / users / spots / agent / trips
│   │   ├── core/                   # security（JWT/bcrypt）、deps（当前用户）
│   │   ├── knowledge_base/         # 景点与攻略种子数据 + 注入逻辑
│   │   ├── llm/client.py           # OpenAI 兼容客户端封装
│   │   ├── models/                 # ORM：user / spot / trip / booking / preference
│   │   ├── rag/                    # chain / embeddings / vectorstore
│   │   ├── schemas/                # Pydantic 出入参
│   │   ├── services/               # spot_service / trip_service
│   │   └── utils/helpers.py        # 日期解析等工具
│   ├── scripts/
│   │   ├── init_db.py              # 建表
│   │   └── seed_data.py            # 灌入种子数据
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.ts / App.vue       # 应用外壳（顶栏 / 导航 / 路由出口）
│   │   ├── api/                    # http / auth / spot / trip
│   │   ├── router/index.ts         # 路由与登录守卫
│   │   └── stores/user.ts          # Pinia 用户态
│   ├── vite.config.ts              # dev 端口 5173，/api 代理至 127.0.0.1:8000
│   └── package.json
└── data/                           # 运行时生成：SQLite + ChromaDB（已在 .gitignore 中排除）
```

---

## 四、Agent 工作流

```
parse_requirements ──► search_spots ──► fetch_weather ──► generate_itinerary
                                                                 │
                                          ┌──────────────────────┴───────────────┐
                                          │ 出错且未产出回复 → 重试（最多 3 次）      │
                                          │ 否则            → proceed            │
                                          └──────────────────────┬───────────────┘
                                                                 ▼
                                                    optimize_route ──► generate_response ──► END
```

- **parse_requirements**：从自然语言抽取目的地、起止日期、预算、人数、出行风格。
- **search_spots**：RAG 召回景点与攻略（`RAG_TOP_K` 默认 20）。
- **fetch_weather**：查询目的地天气（未配置天气 API 时给出合理缺省）。
- **generate_itinerary**：LLM 生成逐日行程草案；失败回退规则引擎。
- **optimize_route**：按地理邻近与时段合理性重排动线。
- **generate_response**：成文输出，并附建议操作（`suggested_actions`）。

---

## 五、快速开始

### 1. 后端

```bash
cd backend

# 创建虚拟环境（可选）
python -m venv .venv && .venv\Scripts\activate      # Windows
# source .venv/bin/activate                          # macOS / Linux

pip install -r requirements.txt

# 配置环境变量
copy .env.example .env                               # Windows
# cp .env.example .env                               # macOS / Linux
# 编辑 .env，至少填入一个可用的 LLM Key（见下方说明）

# 启动
uvicorn app.main:app --reload --port 8000
```

启动后：

- 接口文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>
- 首次启动会自动建表、创建默认管理员（`admin` / `admin123456`，可用环境变量 `ADMIN_PASSWORD` 覆盖）、并注入景点与攻略知识库。

### 2. 前端

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173，/api 自动代理到 8000 端口
```

生产构建：

```bash
npm run build        # 产物输出到 frontend/dist，后端会自动托管该目录
```

---

## 六、环境变量

完整清单见 `backend/.env.example`，关键项：

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DATABASE_URL` | 数据库连接串（留空则用项目根 `data/travelai.db` 绝对路径） | `sqlite:///<项目根>/data/travelai.db` |
| `SECRET_KEY` | JWT 签名密钥（**上线务必更换**） | `travelai-dev-secret-change-in-production` |
| `ADMIN_PASSWORD` | 首次启动创建的默认管理员口令 | `admin123456` |
| `LLM_PROVIDER` | `openai` / `deepseek` / `qwen` / `none` | `deepseek` |
| `LLM_API_KEY` | 统一 Key，显式填写时优先级最高 | 空 |
| `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `QWEN_API_KEY` | 各供应商独立 Key | 空 |
| `LLM_MODEL` | 模型名 | `deepseek-chat` |
| `EMBEDDING_MODEL` | 默认 `hash-ngram-384`（零依赖）；配远端时走 OpenAI 兼容 embedding | `hash-ngram-384` |
| `VECTOR_STORE_TYPE` | `chroma` / `memory` | `chroma` |
| `RAG_TOP_K` | 检索召回条数 | `20` |
| `SKIP_SEED` | `true` 时启动跳过知识库注入 | `false` |
| `AMAP_API_KEY` / `WEATHER_API_KEY` / `FLIGHT_API_KEY` | 可选外部数据源 | 空 |

> `.env` 位于 `backend/` 目录（与 `.env.example` 同级），由 `app/config.py` 以绝对路径加载，因此从任意工作目录启动都能读到。

> **无 Key 也能跑**：不填任何 LLM Key 时，Agent 自动降级到规则引擎模式，仍可生成结构完整的行程，便于本地演示与自动化测试。

---

## 七、主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health`、`/api/health` | 健康检查（含 LLM 是否就绪、向量库类型） |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录，返回 JWT |
| GET | `/api/users/me` | 当前用户信息 |
| GET | `/api/spots` | 景点检索 |
| POST | `/api/agent/chat` | 与旅行 Agent 对话 |
| POST | `/api/agent/generate-trip` | 一键生成行程并落库 |
| GET/POST | `/api/trips` | 我的行程列表 / 新建 |
| WS | `/api/ws/progress` | 规划进度实时通道 |

---

## 八、设计取舍

- **默认 SQLite**：零配置开箱即用，`DATABASE_URL` 可无缝切 PostgreSQL。
- **默认哈希向量**：`hash-ngram-384` 不依赖任何模型下载，保证离线可跑；需要语义精度时换远端 embedding。
- **上下文装配在配置层完成**：`Settings.resolved_llm` 统一解析供应商，节点代码不感知具体厂商。
- **`env_file` 使用绝对路径**：避免从其它工作目录启动时读不到 `.env`。
- **知识库注入失败不阻塞启动**：DB / 向量库异常时服务仍可用，仅日志告警。
