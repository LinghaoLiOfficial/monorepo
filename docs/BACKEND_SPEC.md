# 后端架构与工程规范法典

> 适用范围：Python + FastAPI 后端服务。  
> 使用对象：AI 编码智能体、人类后端开发者、代码审查者。  
> 核心目标：用确定的技术选型、清晰的分层边界和可执行的工程约束，降低 AI 生成代码时的架构漂移。

---

## 0. 规范关键词

- **MUST**：必须遵守，违反视为架构错误。
- **MUST NOT**：禁止行为。
- **允许例外**：只有经过明确架构审查后才能偏离本规范。

---

## 1. 确定技术栈基线

### 1.1 运行时、框架与部署

- **语言版本**：Python `>=3.12`。
- **Web 框架**：FastAPI。
- **ASGI 运行**：Uvicorn。
- **生产部署平台**：Docker Compose。
- **生产部署方式**：生产环境 MUST 使用 Docker 镜像部署。
- **应用进程**：MUST 使用 `uvicorn` 启动 FastAPI。
- **多进程并发**：MUST 通过 `uvicorn --workers` 配置。
- **Docker 基础镜像**：MUST 使用 `python:3.12-slim`。
- **CI/CD**：MUST 使用 GitHub Actions。

### 1.2 包管理与配置

- **包管理**：MUST 使用 `uv`。
- **依赖声明**：MUST 写入 `pyproject.toml`。
- **锁文件**：MUST 使用 `uv.lock`，并提交到版本库。
- **依赖安装**：本地开发、CI、Docker 构建 MUST 使用 `uv sync`。
- **命令执行**：项目脚本 MUST 通过 `uv run` 执行。
- **禁止项**：禁止使用 pipenv、poetry、conda 作为项目主包管理工具。
- **配置管理**：MUST 使用 `pydantic-settings`。
- **配置入口**：所有配置 MUST 通过 `app/core/config.py` 中的 `Settings` 类读取。
- **禁止项**：业务代码禁止直接调用 `os.getenv()` 读取配置。

### 1.3 数据库、ORM 与迁移

- **主数据库**：生产、开发、测试环境 MUST 统一使用 PostgreSQL。
- **ORM**：MUST 使用 SQLAlchemy 2.x。
- **数据库会话**：异步服务 MUST 使用 `AsyncSession`。
- **迁移工具**：MUST 使用 Alembic。
- **测试数据库**：测试环境 MUST 使用独立 PostgreSQL 测试库。
- **禁止项**：禁止使用 SQLite 代替 PostgreSQL 做集成测试。
- **PostgreSQL 扩展策略**：所有 PostgreSQL 扩展 MUST 按需启用；项目模板默认不启用非必要扩展。

### 1.4 外部请求、任务与缓存

- **异步 HTTP Client**：MUST 使用 `httpx.AsyncClient`。
- **重试**：MUST 使用 `tenacity`，并配置最大重试次数、退避策略和 timeout。
- **后台任务队列**：MUST 使用 Procrastinate。
- **任务存储**：任务定义、任务状态、任务锁、延迟执行、周期任务和重试状态 MUST 存储在 PostgreSQL。
- **缓存策略**：默认不引入 Redis、Memcached 或其他独立缓存服务。
- **持久化缓存**：MUST 使用 PostgreSQL 表、物化视图、索引、反范式字段或计算结果表。
- **进程内缓存**：MUST 使用 `functools.lru_cache` 或 `cachetools`，仅用于配置、静态字典和低频非敏感元数据。

### 1.5 日志、可观测性与质量工具

- **日志系统**：MUST 使用 `structlog`。
- **日志格式**：MUST 输出结构化 JSON 日志。
- **第三方库日志**：MUST 通过 Python 标准库 `logging` 接入并桥接到 `structlog`。
- **禁止项**：禁止使用 `loguru` 作为项目主日志系统。
- **可观测性**：生产服务 MUST 接入 OpenTelemetry。
- **指标格式**：metrics MUST 暴露为 Prometheus 格式。
- **Lint**：MUST 使用 `ruff check`。
- **格式化**：MUST 使用 `ruff format`。
- **Import 排序**：MUST 使用 Ruff 的 `I` 规则。
- **类型检查**：MUST 使用 `mypy`。
- **测试框架**：MUST 使用 `pytest` + `pytest-asyncio`。
- **覆盖率**：MUST 使用 `pytest-cov`。
- **禁止项**：禁止同时引入 Black、isort、pyright 作为强制质量门禁工具。

---

## 2. 架构原则

### 2.1 标准调用链路

所有业务请求 MUST 遵循：

```text
API Router -> Application Service / Use Case -> Domain -> Port Interface -> Infrastructure Adapter
```

职责边界：

- **API 层**：只处理 HTTP 协议、鉴权依赖、请求 DTO、响应 DTO、状态码和路由声明。
- **Application 层**：负责编排用例、事务边界、调用 Repository 接口、调用 External Client 接口、触发后台任务。
- **Domain 层**：保存业务实体、值对象、领域规则、领域错误和纯业务算法。
- **Infrastructure 层**：实现数据库、第三方 API、缓存、任务队列、文件存储、邮件发送等具体技术。

### 2.2 依赖方向

MUST 遵守以下依赖方向：

```text
api -> application -> domain
infrastructure -> application/domain
```

MUST NOT：

- `domain` 导入 `infrastructure`。
- `domain` 直接依赖 SQLAlchemy、PostgreSQL Client、httpx、第三方 SDK。
- `api` 直接调用 ORM Model、Repository 具体实现或第三方 SDK。
- Application Service 直接 new 具体外部 Client；必须依赖接口或协议。

### 2.3 业务逻辑归属

- 领域算法、价格计算、权限判定、状态机、业务规则 MUST 放在 `domain/`。
- 用例编排、事务、调用多个仓储或外部服务 MUST 放在 `application/`。
- `utils/` 只允许放通用、无业务语义的纯函数，例如时间格式、哈希、分页工具。
- MUST NOT 把复杂业务逻辑放进 `utils/`。

### 2.4 异步优先

- 所有数据库、HTTP、缓存、文件、队列等 I/O 操作 MUST 使用 async 版本。
- MUST NOT 在 async route / async service 中执行阻塞 I/O。
- CPU 密集型任务 MUST 移出请求链路，交给 Procrastinate worker、进程池或专用计算服务。

### 2.5 事务边界

- 事务边界 MUST 位于 Application Service / Use Case 层。
- Repository 不得自行提交事务，除非该方法被明确设计为独立事务。
- 一个业务用例内涉及多个写操作时，MUST 保证原子性。

---

## 3. 标准目录结构

```text
backend/
  ├── app/
  │   ├── main.py
  │   ├── core/
  │   │   ├── config.py
  │   │   ├── logging.py
  │   │   ├── exceptions.py
  │   │   ├── middleware.py
  │   │   ├── security.py
  │   │   └── observability.py
  │   ├── api/
  │   │   ├── deps.py
  │   │   └── v1/
  │   │       ├── router.py
  │   │       └── users.py
  │   ├── application/
  │   │   ├── services/
  │   │   ├── use_cases/
  │   │   ├── ports/
  │   │   │   ├── repositories.py
  │   │   │   └── external_clients.py
  │   │   └── dto/
  │   ├── domain/
  │   │   ├── entities/
  │   │   ├── value_objects/
  │   │   ├── enums/
  │   │   ├── errors.py
  │   │   └── policies/
  │   ├── infrastructure/
  │   │   ├── db/
  │   │   │   ├── session.py
  │   │   │   ├── models/
  │   │   │   └── repositories/
  │   │   ├── external/
  │   │   ├── cache/
  │   │   ├── queue/
  │   │   │   ├── app.py
  │   │   │   ├── worker.py
  │   │   │   └── tasks/
  │   │   ├── storage/
  │   │   │   └── aliyun_oss.py
  │   │   └── email/
  │   │       └── smtp_client.py
  │   ├── schemas/
  │   │   ├── common.py
  │   │   └── users.py
  │   └── utils/
  ├── alembic/
  ├── tests/
  │   ├── unit/
  │   ├── integration/
  │   └── e2e/
  ├── scripts/
  ├── docker-compose.yml
  ├── Dockerfile
  ├── pyproject.toml
  ├── uv.lock
  ├── alembic.ini
  ├── .env.example
  └── README.md
```

---

## 4. API 契约规范

### 4.1 路由规范

- 所有业务 API MUST 带版本前缀：`/api/v1/...`。
- 资源命名 MUST 使用复数名词：`/api/v1/users`、`/api/v1/orders`。
- 动作类接口必须谨慎使用动词，例如 `/api/v1/orders/{order_id}/cancel`。

### 4.2 请求与响应 DTO

- API 入参和出参 MUST 使用 Pydantic Schema。
- API 层 MUST NOT 直接暴露 ORM Model。
- Response Schema MUST 显式声明，避免把内部字段泄漏给前端。
- 创建、更新、局部更新、响应模型 MUST 拆分为不同 Schema。

### 4.3 统一响应包装

所有业务 API 的成功响应 MUST 使用统一结构：

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "request_id": "xxx"
}
```

所有业务 API 的错误响应 MUST 使用统一结构：

```json
{
  "code": "USER_NOT_FOUND",
  "message": "User not found",
  "details": {},
  "request_id": "xxx"
}
```

允许不使用统一业务响应包装的接口：

- 文件下载。
- 流式响应。
- WebSocket。
- Prometheus metrics。
- OpenAPI docs。
- 健康探测接口。
- `204 No Content`。
- 第三方 webhook 回调必须遵守对方协议的响应。

### 4.4 HTTP 状态码

- `200`：查询或普通成功。
- `201`：资源创建成功。
- `202`：请求已接受，异步处理中。
- `204`：成功但无响应体。
- `400`：客户端请求语义错误。
- `401`：未认证或 token 无效。
- `403`：已认证但无权限。
- `404`：资源不存在。
- `409`：资源冲突，例如唯一键冲突、状态冲突。
- `422`：请求格式或字段校验失败。
- `429`：触发限流。
- `500`：未预期服务器错误。
- `502/503/504`：上游服务错误、不可用或超时。

### 4.5 分页规范

- 业务列表接口默认 MUST 使用 cursor pagination。
- cursor pagination 的请求参数 MUST 使用：`cursor`、`limit`。
- cursor pagination 的响应数据 MUST 包含：`items`、`next_cursor`、`has_more`。
- 后台管理类低频列表允许使用 `page` / `page_size`。
- `page_size` 和 `limit` MUST 设置最大值，禁止无边界返回。
- 排序字段 MUST 固定白名单，禁止前端传任意数据库字段名。

---

## 5. 数据库与持久化规范

### 5.1 SQLAlchemy 模型

- MUST 使用 SQLAlchemy 2.x 声明式写法：`Mapped` + `mapped_column`。
- 所有业务表 MUST 包含：
  - `id`：主键，字段类型 MUST 使用 PostgreSQL `uuid`，生成策略 MUST 使用 UUIDv7。
  - `created_at`。
  - `updated_at`。
- 禁止新业务表使用自增 BIGINT 作为主键。
- 外部 API 暴露的资源 ID MUST 使用 UUID 字符串。
- 所有数据库时间字段 MUST 使用 timezone-aware datetime。
- 数据库存储 MUST 统一使用 UTC。
- API 输出时间 MUST 使用 ISO 8601 格式。
- 时间字段命名 MUST 使用 `created_at`、`updated_at`、`expires_at`。
- 禁止在数据库中存储本地时区时间字符串。

### 5.2 Repository 规范

- Repository 只负责数据访问，不写业务规则。
- Repository 方法名 MUST 表达数据语义，例如 `get_by_email`、`list_active_by_org_id`。
- Repository MUST NOT 返回未经控制的 ORM 对象到 API 层。
- 查询必须考虑分页、排序、索引和 N+1 问题。

### 5.3 数据库连接池规范

Async SQLAlchemy engine MUST 显式配置以下参数：

- `pool_size`。
- `max_overflow`。
- `pool_timeout`。
- `pool_recycle`。
- `statement_timeout`。
- `idle_in_transaction_session_timeout`。

配置要求：

- Web 进程、Procrastinate worker、Alembic migration、脚本任务 MUST 分别评估连接数。
- 所有连接数总和 MUST 小于 PostgreSQL `max_connections` 的安全上限。
- `statement_timeout` MUST 防止慢查询长期占用连接。
- `idle_in_transaction_session_timeout` MUST 防止事务空闲导致锁长期持有。
- 连接池配置 MUST 放在 `core/config.py` 的 `Settings` 中。

### 5.4 Alembic 迁移策略

- 所有 schema 变更 MUST 通过 Alembic migration。
- 所有 migration MUST 命名，命名必须体现业务意图。
- 禁止提交空 migration。
- migration 文件 MUST 经过人工审查。
- 大表迁移 MUST 分阶段执行。
- 数据回填 MUST 使用独立脚本或 Procrastinate 后台任务执行。
- 自动生成 migration 后 MUST 检查字段类型、索引、约束命名、默认值和数据回填逻辑。

### 5.5 查询性能

- 高频查询字段 MUST 建索引。
- 唯一业务键 MUST 显式唯一约束。
- 列表接口 MUST 支持分页。
- 禁止无边界查询全表数据。
- 禁止在无索引字段上执行高频过滤、排序或限流查询。

### 5.6 PostgreSQL 多模型数据使用规范

本项目所有持久化数据源默认统一收敛到 PostgreSQL，不单独引入 MongoDB、Neo4j、Elasticsearch、RedisGraph 或独立向量数据库，除非经过单独架构审查。

#### 5.6.1 关系型数据

- 普通业务实体、交易数据、用户数据、订单数据、权限数据 MUST 使用标准关系表建模。
- 强一致写入、事务、唯一约束、外键约束和复杂筛选 MUST 优先使用关系模型。
- Repository 层 MUST 使用 SQLAlchemy 2.x async 查询。

#### 5.6.2 文档型 JSON 数据

- 半结构化、字段变化频繁、第三方原始 payload、审计快照使用 PostgreSQL `JSONB` 字段。
- 可查询 JSON 字段 MUST 建立表达式索引或 GIN 索引。
- 稳定核心业务字段 MUST 拆成普通列，禁止把核心业务实体整体塞进 `JSONB`。

#### 5.6.3 树形与层级数据

- 简单层级 MUST 使用邻接表 `parent_id` + 递归 CTE。
- 高频祖先/后代查询 MUST 按需启用 PostgreSQL `ltree` 扩展。
- 层级深度、循环引用和级联处理规则 MUST 在 Domain Policy 中明确。

#### 5.6.4 图关系数据

- 轻中度图关系 MUST 使用 PostgreSQL 关系表建模：
  - 节点表：`*_nodes` 或业务实体表。
  - 边表：`*_edges`，包含 `source_id`、`target_id`、`edge_type`、`weight`、`metadata`。
  - 遍历查询：使用递归 CTE。
- 需要 Cypher 风格查询或更接近图数据库的表达能力时，MUST 按需启用 PostgreSQL 扩展 Apache AGE。
- 超深层、多跳、高并发、复杂图算法场景 MUST 先做基准测试，再决定是否继续使用 PostgreSQL 图能力。

#### 5.6.5 全文搜索

- 站内搜索、标题/正文搜索、标签搜索默认 MUST 使用 PostgreSQL Full Text Search。
- 模糊搜索 MUST 按需启用 `pg_trgm`。
- 搜索字段 MUST 使用 `tsvector` 生成列或物化字段。
- 高频搜索 MUST 使用 GIN 索引。

#### 5.6.6 地理空间数据

- 地理位置、附近搜索、围栏、多边形、距离计算 MUST 按需启用 PostGIS。
- 经纬度数据 MUST 明确 SRID。
- 高频空间查询 MUST 使用 GiST 或 SP-GiST 索引。

#### 5.6.7 向量检索

- AI embedding、语义搜索、相似度匹配 MUST 按需启用 PostgreSQL `pgvector` 扩展。
- 向量维度、距离函数、索引类型和召回策略 MUST 在模块设计中明确。
- 向量数据必须与业务主键关联，禁止出现无法追溯来源的孤立向量。

---

## 6. 外部依赖、任务、文件与邮件规范

### 6.1 External Client 封装

- 第三方 SDK、外部 API、支付、邮件、对象存储等 MUST 封装在 `infrastructure/` 对应 adapter 中。
- Application 层 MUST 依赖 `application/ports/external_clients.py` 中定义的接口或 Protocol。
- API 和 Domain 层 MUST NOT 直接导入第三方 SDK。

### 6.2 Timeout、Retry 与错误映射

每个外部调用 MUST 配置：

- connect timeout。
- read timeout。
- 最大重试次数。
- 指数退避和 jitter。
- 可重试错误白名单。
- 上游错误到本地业务错误的映射。

MUST NOT：

- 对非幂等外部写请求盲目重试。
- 对用户态 4xx 错误重试。
- 无限重试。

### 6.3 后台任务队列规范：Procrastinate + PostgreSQL

本项目后台任务队列 MUST 使用 Procrastinate，并统一基于 PostgreSQL 存储任务状态。

#### 6.3.1 适用场景

Procrastinate MUST 用于：

- 邮件发送。
- Webhook 投递与重试。
- 文件处理、导入导出、报表生成。
- AI 任务编排、embedding 生成、异步摘要生成。
- 延迟执行任务。
- 周期任务。
- 需要可靠重试的外部 API 调用。

FastAPI `BackgroundTasks` 只能用于请求结束后立即执行的非关键短任务，且禁止用于订单、通知、数据同步、AI 任务等需要可靠投递的业务。

#### 6.3.2 任务设计规范

- 任务参数 MUST 可 JSON 序列化。
- 任务参数 MUST 只传业务主键，不传大对象或完整 ORM 数据。
- 任务 MUST 具备幂等性。
- 涉及外部写操作的任务 MUST 使用业务幂等键。
- 任务内部 MUST 重新打开数据库 session，禁止复用请求链路中的 `AsyncSession`。
- 任务失败 MUST 抛出显式异常，禁止吞异常。
- 任务日志 MUST 带 `job_id`、`queue`、`task_name`、`request_id` 或业务关联 ID。

#### 6.3.3 Worker 运行规范

- 生产环境 MUST 独立运行 Procrastinate worker 进程。
- Web 进程和 Worker 进程 MUST 使用同一份代码镜像，但使用不同启动命令。
- Worker 并发数 MUST 根据 PostgreSQL 最大连接数、任务 I/O 类型和 CPU 使用情况配置。
- Worker 必须支持优雅关闭。

#### 6.3.4 队列运维规范

- Procrastinate 队列表属于高写入、高更新数据表，MUST 监控表膨胀、dead tuples、autovacuum、队列堆积和任务失败率。
- 已完成任务 MUST 配置清理策略，避免任务表无限增长。
- 大批量任务入队 MUST 分批提交。

### 6.4 文件存储规范：阿里云 OSS + PostgreSQL 元数据

- 所有文件类型 MUST 存储到阿里云 OSS。
- PostgreSQL MUST 存储文件元数据。
- 业务文件内容禁止存储到 PostgreSQL `BYTEA` 或 Large Object。
- 文件上传、下载、预览、导入导出 MUST 通过 `infrastructure/storage/aliyun_oss.py` 封装。
- API 层和 Domain 层禁止直接调用阿里云 OSS SDK。

PostgreSQL 文件元数据表 MUST 至少包含：

- `id`：UUIDv7。
- `bucket`。
- `object_key`。
- `original_filename`。
- `content_type`。
- `size_bytes`。
- `checksum`。
- `etag`。
- `owner_user_id` 或业务归属 ID。
- `created_at`。
- `updated_at`。

文件访问规范：

- 私有文件 MUST 使用后端鉴权后生成短有效期签名 URL。
- 文件上传 MUST 校验大小、类型、扩展名和业务归属。
- 文件下载 MUST 校验资源级权限。
- 大文件上传 MUST 使用分片上传。
- 文件处理任务 MUST 通过 Procrastinate 执行。

### 6.5 邮件发送规范：SMTP

- 邮件发送 MUST 使用 SMTP。
- SMTP 配置 MUST 通过 `pydantic-settings` 注入。
- 邮件发送 MUST 封装在 `infrastructure/email/smtp_client.py`。
- 业务代码 MUST 通过 Application 层端口调用邮件能力。
- 邮件发送任务 MUST 通过 Procrastinate 执行。
- 邮件发送失败 MUST 记录失败原因，并按任务重试策略重试。
- 邮件模板 MUST 与发送逻辑分离。

### 6.6 Webhook 规范

- Webhook 签名算法 MUST 使用 HMAC-SHA256。
- Webhook 请求 MUST 包含 timestamp。
- Webhook 事件 MUST 包含 event_id。
- 接收方校验 MUST 覆盖签名、timestamp 时效性和 event_id 去重。
- event_id 幂等记录 MUST 存储在 PostgreSQL。
- Webhook 投递日志 MUST 存储在 PostgreSQL。
- Webhook 投递失败 MUST 通过 Procrastinate 重试。
- Webhook payload MUST 记录脱敏后的必要调试信息。

---

## 7. 配置与密钥管理

- 配置管理 MUST 使用 `pydantic-settings`。
- 所有配置 MUST 通过 `app/core/config.py` 中的 `Settings` 类读取。
- 业务代码禁止直接调用 `os.getenv()` 读取配置。
- `.env` 仅允许用于本地开发，MUST NOT 提交真实 `.env`。
- MUST 提供 `.env.example`。
- 生产环境 MUST 通过 Docker Compose 环境变量或密钥管理系统注入配置。
- 不同环境 MUST 使用明确环境名：`local`、`test`、`staging`、`production`。
- 启动时 MUST 校验关键配置，例如数据库 URL、JWT RS256 私钥/公钥、阿里云 OSS 配置、SMTP 配置、外部服务 endpoint。
- 日志、错误响应和测试快照中 MUST 脱敏 secret、token、password、cookie、authorization header。

---

## 8. 安全规范

### 8.1 认证与 Token 策略

- API 认证 MUST 使用 JWT Bearer Token。
- 默认前后端鉴权传递方式 MUST 使用 HTTP Header：`Authorization: Bearer <token>`。
- 浏览器应用如需使用 Cookie，必须单独设计 CSRF 防护。
- JWT 签名算法 MUST 使用 RS256。
- Access Token MUST 使用短有效期。
- Refresh Token MUST 存储在 PostgreSQL，并支持吊销、轮换和过期。
- 密码哈希 MUST 使用 Argon2id。
- 认证逻辑 MUST 放在 `core/security.py` 或专用 `auth` 模块。
- API 层 MUST 使用依赖注入获取当前用户。

### 8.2 授权模型

- 权限模型 MUST 使用 RBAC。
- 角色、权限、用户角色关系 MUST 存储在 PostgreSQL。
- 资源级权限 MUST 使用 Domain Policy 校验。
- 多租户系统 MUST 强制 `org_id` / `tenant_id` 数据边界。
- 资源级权限检查 MUST 在 Application 或 Domain Policy 中完成，不能只在前端控制。
- 禁止只在 API Router 或前端做权限判断。

### 8.3 输入与输出安全

- 所有外部输入 MUST 经过 Pydantic 校验。
- MUST 防止 Mass Assignment：请求 DTO 只允许接收可修改字段。
- 响应 DTO MUST 防止敏感字段泄漏。
- 文件上传 MUST 校验大小、类型、扩展名和业务归属。

### 8.4 常见 API 风险

项目 MUST 覆盖以下风险：

- 对象级越权。
- 属性级越权。
- 认证缺陷。
- 资源无限消耗。
- 批量赋值。
- SSRF。
- 敏感信息泄漏。

---

## 9. 缓存规范

### 9.1 默认缓存策略

- 默认不引入 Redis、Memcached 或其他独立缓存服务。
- 应用级缓存 MUST 优先通过 PostgreSQL 表、物化视图、查询优化、索引、反范式字段和合理数据建模解决。
- 持久化缓存、计算结果缓存、报表缓存、权限快照缓存 MUST 存储在 PostgreSQL。
- 缓存表 MUST 明确过期时间、刷新策略、失效策略和清理策略。

### 9.2 进程内缓存

- 进程内短生命周期缓存 MUST 使用 `functools.lru_cache` 或 `cachetools`。
- 进程内缓存只能用于配置、静态字典、低频元数据等非用户敏感数据。
- 禁止使用进程内缓存保存用户会话、权限状态、请求上下文或跨请求可变业务状态。
- 多 worker 部署下，进程内缓存 MUST 被视为每个进程独立、不一致、可随时丢失。

### 9.3 禁止与例外

- 默认禁止引入 Redis、Memcached、Dragonfly、KeyDB 或其他独立缓存中间件。
- 禁止把 PostgreSQL 当作超低延迟内存缓存使用。
- 分布式限流计数、实时排行榜、在线状态、超高频热点 key、pub/sub、低延迟分布式锁等场景如确需 Redis，MUST 经过单独架构审查。

---

## 10. API 限流规范

### 10.1 默认限流方案

- API 限流 MUST 使用 PostgreSQL 表实现。
- 限流维度 MUST 支持 `user_id`、`org_id`、`ip`、`api_key`。
- 默认限流算法 MUST 使用 fixed window 或 sliding window counter，具体接口必须在设计中声明使用哪一种。
- 高频公共接口、登录接口、注册接口、验证码接口、AI 调用接口、Webhook 接收接口 MUST 配置限流。
- 触发限流时 MUST 返回 HTTP `429 Too Many Requests`。
- 限流错误响应 MUST 包含 `request_id`，并包含 `retry_after_seconds`。

### 10.2 限流数据规范

- 限流记录 MUST 存储在 PostgreSQL。
- 限流表 MUST 建立与查询维度匹配的索引。
- 限流计数更新 MUST 保证并发安全。
- 过期限流窗口 MUST 定期清理，防止表无限增长。
- 禁止在无索引字段上执行高频限流查询。

---

## 11. 分布式锁规范

- 分布式锁 MUST 使用 PostgreSQL advisory lock。
- 禁止默认引入 Redis、ZooKeeper、etcd 或其他锁服务。
- advisory lock MUST 用于定时任务互斥、资源级并发控制、批处理任务防重。
- 锁 key 生成规则 MUST 稳定、可读、无冲突。
- 持锁逻辑 MUST 设置超时边界，禁止长时间占用锁。
- 获取锁失败的业务行为 MUST 明确：跳过、重试或返回冲突错误。

---

## 12. 日志、追踪与可观测性

### 12.1 Request ID

- 每个请求 MUST 生成或透传 `request_id`。
- 响应体或响应 header MUST 返回 `request_id`。
- 所有日志 MUST 带 `request_id`。

### 12.2 结构化日志

- MUST 使用 `structlog` 输出结构化 JSON 日志。
- 日志字段 MUST 包含：
  - `timestamp`
  - `level`
  - `service`
  - `env`
  - `request_id`
  - `message`
  - `path`
  - `method`
  - `status_code`
  - `duration_ms`
- 已认证请求日志 MUST 包含 `user_id`。
- 业务关键事件 MUST 记录独立 `event_name`。

### 12.3 OpenTelemetry 与 Prometheus

生产服务 MUST 使用 OpenTelemetry 采集 tracing 与 metrics，并暴露 Prometheus 格式指标。

必须覆盖：

- HTTP 请求总量、错误率、延迟分布。
- SQLAlchemy 数据库查询耗时。
- `httpx` 外部 API 调用耗时、错误率、超时率。
- Procrastinate 任务队列积压量、成功率、失败率、重试次数。
- 阿里云 OSS 上传、下载、失败率和耗时。
- SMTP 发送成功率、失败率和耗时。
- Webhook 投递成功率、失败率、重试次数。
- 关键业务指标。

日志、trace、metrics MUST 通过 `request_id` / `trace_id` 关联。

---

## 13. 测试规范

### 13.1 测试分层

- **Unit Tests**：测试 Domain、纯函数、策略类、Application Service 的业务分支；外部 I/O 必须 mock。
- **Integration Tests**：测试 Repository、数据库约束、migration、外部 client adapter 的协议处理。
- **E2E Tests**：覆盖核心用户路径，数量少但稳定。

### 13.2 异步测试

- async 函数测试 MUST 使用 `pytest-asyncio`。
- FastAPI 测试 MUST 使用 `httpx.AsyncClient + ASGITransport`。
- 禁止使用同步 `TestClient` 作为默认 API 测试客户端。
- 每个测试 MUST 隔离数据状态。
- 集成测试 MUST 连接独立 PostgreSQL 测试库。

### 13.3 覆盖率要求

- Domain 和 Application 层 MUST 有高覆盖率。
- 安全、权限、状态机、订单等关键路径 MUST 覆盖成功、失败和边界场景。
- 覆盖率不能替代测试质量；禁止只为覆盖率编写无断言测试。

---

## 14. 代码风格与质量门禁

### 14.1 类型注解

- 公共函数、Service 方法、Repository 方法 MUST 标注参数和返回类型。
- 禁止无理由使用 `Any`。
- 复杂 dict MUST 定义 TypedDict、Pydantic Model 或 dataclass。

### 14.2 命名规范

- 文件与模块：`snake_case.py`。
- 类、异常、Pydantic Schema：`PascalCase`。
- 函数与变量：`snake_case`。
- 常量：`UPPER_SNAKE_CASE`。
- 异步函数命名不强制加 `async_`，但语义必须清晰。

### 14.3 注释与文档

- 公共类和公共函数 MUST 有 docstring。
- 注释解释“为什么”，不要重复代码“是什么”。
- 复杂业务规则 MUST 在 Domain Policy 或 Application Service 附近写清楚业务假设。

### 14.4 CI 质量门禁

每次提交 MUST 通过以下 GitHub Actions 质量门禁：

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy app tests
uv run pytest
```

---

## 15. AI 编码智能体执行规则

当 AI 编写或修改后端代码时，MUST 遵守以下流程。

### 15.1 修改前

AI MUST 先识别：

- 本次需求属于哪个业务用例。
- 需要修改哪些层：API、Application、Domain、Infrastructure、Schema、Migration、Tests。
- 是否涉及数据库 schema 变更。
- 是否涉及权限、并发、外部调用、文件、邮件、任务或 Webhook。

### 15.2 修改中

AI MUST：

- 先定义或更新 Schema / DTO。
- 再定义 Application Service / Use Case。
- 再补充 Domain 规则。
- 再实现 Repository 或 External Adapter。
- 再补充 API Router。
- 最后补测试与迁移。

AI MUST NOT：

- 为了快速实现而让 API 直接访问数据库。
- 把业务规则塞进路由函数。
- 绕过接口直接调用第三方 SDK。
- 生成没有测试的关键业务逻辑。
- 吞掉异常或返回模糊错误。

### 15.3 输出代码后

AI MUST 给出：

- 修改文件列表。
- 是否需要 migration。
- 需要运行的测试命令。
- 可能的风险点。
- 尚未覆盖的边界情况。

---

## 16. 功能交付验收清单

每个后端功能合并前，MUST 确认：

- [ ] API 路由带 `/api/v1` 版本前缀。
- [ ] 所有业务 API 使用统一成功与错误响应结构。
- [ ] 列表接口使用 cursor pagination；后台管理低频列表可使用 `page` / `page_size`。
- [ ] Request / Response Schema 明确。
- [ ] API 没有直接访问 ORM 或第三方 SDK。
- [ ] 业务逻辑不在路由层。
- [ ] Domain 不依赖 Infrastructure。
- [ ] Repository 不提交不属于自己的事务。
- [ ] 新业务表主键使用 UUIDv7，字段名为 `id`，数据库类型为 PostgreSQL `uuid`。
- [ ] 所有时间字段使用 timezone-aware datetime，数据库统一存储 UTC，API 输出 ISO 8601。
- [ ] 数据库变更有 Alembic migration。
- [ ] migration 已命名，且不是空 migration。
- [ ] 大表迁移已分阶段设计。
- [ ] 数据回填使用独立脚本或 Procrastinate 后台任务。
- [ ] 查询有分页、索引和边界限制。
- [ ] 数据库连接池配置覆盖 `pool_size`、`max_overflow`、`pool_timeout`、`pool_recycle`、`statement_timeout`、`idle_in_transaction_session_timeout`。
- [ ] 外部调用有 timeout、retry 和错误映射。
- [ ] 文件内容存储到阿里云 OSS，PostgreSQL 仅保存文件元数据。
- [ ] 邮件通过 SMTP，并由 Procrastinate 任务发送。
- [ ] Webhook 使用 HMAC-SHA256、timestamp、event_id、PostgreSQL 投递日志和 Procrastinate 重试。
- [ ] 权限检查覆盖对象级和租户级边界。
- [ ] 限流使用 PostgreSQL 表实现，并对高频接口启用。
- [ ] 分布式锁使用 PostgreSQL advisory lock。
- [ ] 错误响应脱敏，日志保留 request_id。
- [ ] 单元测试和必要的集成测试已补充。
- [ ] FastAPI API 测试使用 `httpx.AsyncClient + ASGITransport`。
- [ ] `ruff`、`mypy`、`pytest` 通过。

---

## 17. 本地开发与依赖管理

### 17.1 依赖管理

- 项目 MUST 使用 `uv` 管理 Python 版本、虚拟环境、依赖解析和锁文件。
- 新增运行时依赖 MUST 使用 `uv add <package>`。
- 新增开发依赖 MUST 使用 `uv add --dev <package>`。
- 安装依赖 MUST 使用 `uv sync`。
- 执行 Python 命令 MUST 使用 `uv run`。
- 禁止手动编辑锁文件。

### 17.2 常用命令

```bash
uv sync
uv run ruff check .
uv run ruff format .
uv run mypy app tests
uv run pytest
```

---

## 18. 推荐最小实现顺序

新项目初始化时，按以下顺序落地：

1. `pyproject.toml` 与 `uv.lock`：依赖声明与锁文件。
2. `Dockerfile`：基于 `python:3.12-slim`。
3. `docker-compose.yml`：生产部署入口。
4. GitHub Actions：CI/CD 质量门禁。
5. `core/config.py`：配置与环境变量。
6. `core/logging.py`：`structlog` 结构化日志与 request_id。
7. `core/exceptions.py`：统一错误与异常处理。
8. `core/security.py`：JWT RS256、Bearer Token、Argon2id。
9. `infrastructure/db/session.py`：异步数据库连接、连接池和 session 依赖。
10. Alembic 初始化与首个 migration。
11. Procrastinate 初始化与 worker 启动入口。
12. 阿里云 OSS 文件存储 adapter。
13. SMTP 邮件 adapter。
14. OpenTelemetry、Prometheus metrics。
15. pytest、pytest-asyncio、独立 PostgreSQL 测试库 fixture。
16. 第一个业务模块：Schema -> Domain -> Port -> Infrastructure -> Application -> API。

---

## 19. 项目脚手架模板要求

本节定义脚手架的**能力边界和禁止项**。`/setup` 的执行模型为默认单流程：项目名注入（Project Name Injection）→ 预检（Preflight）→ 最小补齐（Reconcile）→ 验证（Verify）。具体文件列表、目录结构和文件内容由 `.agents/skills/setup/SKILL.md` 维护，两者以 Skill 为准，本节不重复列举。

### 19.1 脚手架必须覆盖的基础能力

脚手架模板 MUST 覆盖以下基础能力：

- `pyproject.toml`：声明 Python 版本、运行依赖、开发依赖、Ruff、mypy、pytest 配置。
- `uv.lock`：锁文件，MUST 提交到版本库。
- `Dockerfile`：基于 `python:3.12-slim`，使用 `uv sync` 安装依赖。
- `docker-compose.yml`：定义 API、PostgreSQL、Procrastinate worker 服务。
- GitHub Actions CI：执行 `uv sync`、`ruff check`、`ruff format --check`、`mypy`、`pytest`。
- `core/config.py`：基于 `pydantic-settings` 的唯一配置入口。
- `core/logging.py`：基于 `structlog` 的 JSON 日志配置。
- `core/exceptions.py`：统一业务异常、错误码和响应转换。
- `core/middleware.py`：request_id、耗时统计、异常上下文。
- `core/security.py`：JWT RS256、Bearer Token、Argon2id 密码哈希。
- `core/observability.py`：OpenTelemetry 与 Prometheus metrics 初始化，参数类型 MUST 使用 `FastAPI`，不得使用裸 `any`。
- `infrastructure/db/session.py`：Async SQLAlchemy engine、连接池参数、`AsyncSession` 依赖。
- `infrastructure/queue/app.py` 与 `worker.py`：Procrastinate app 与 worker 入口。
- `infrastructure/storage/aliyun_oss.py`：阿里云 OSS 文件存储 adapter。
- `infrastructure/email/smtp_client.py`：SMTP 邮件发送 adapter。
- `schemas/common.py`：统一成功响应、错误响应、分页响应模型。
- `alembic/script.py.mako`：Alembic 迁移模板，MUST 包含完整 `upgrade()` / `downgrade()` 结构。
- `tests/conftest.py`：独立 PostgreSQL 测试库、async session、`httpx.AsyncClient + ASGITransport` fixture。

### 19.2 脚手架禁止项

脚手架模板 MUST NOT：

- 引入 Redis、RabbitMQ、Kafka、Elasticsearch、Neo4j、MongoDB 或独立向量数据库。
- 使用 SQLite 作为集成测试数据库。
- 使用 Black、isort、pyright、poetry、pipenv、conda。
- 使用同步 FastAPI `TestClient` 作为默认测试客户端。
- 在 API 层直接访问 ORM Model 或第三方 SDK。
- 在业务代码中直接调用 `os.getenv()`。
- 把文件内容存储到 PostgreSQL。
- 把完整业务示例写死到模板中；模板只能提供最小可运行骨架。

### 19.3 单一事实来源

脚手架的具体实现（目录结构、文件内容、执行步骤、质量检查清单）MUST 维护在 `.agents/skills/setup/SKILL.md`。

每次本规范的技术选型或约束发生变更时，MUST 同步更新 Skill，并确保 Skill 中的代码通过本规范定义的 GitHub Actions 质量门禁。

## 20. 架构审查触发条件

以下情况 MUST 进行单独架构审查：

- 引入 Redis、RabbitMQ、Kafka、Elasticsearch、Neo4j、MongoDB、独立向量数据库或其他中间件。
- 绕过 Repository 直接写 SQL 到 API 层。
- 绕过阿里云 OSS，把业务文件内容存入 PostgreSQL。
- 绕过 SMTP，引入第三方邮件 API SDK。
- 绕过 Procrastinate，引入新的任务队列。
- PostgreSQL 限流、缓存、任务队列或图查询压测无法满足目标。
- 浏览器应用需要从 Bearer Token 改为 Cookie 鉴权。
- 任何会改变统一响应结构、认证方式、主键策略、部署方式或数据库来源的决策。

