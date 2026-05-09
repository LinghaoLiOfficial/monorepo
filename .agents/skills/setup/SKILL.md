---
description: 一键初始化满足前后端规范的 Monorepo 脚手架（FastAPI 后端 + Next.js 前端）
---

# init-monorepo Skill

## 前置条件

执行前必须读取并理解以下规范文件：

- `docs/BACKEND_SPEC.md`：后端架构法典
- `docs/FRONTEND_SPEC.md`：前端架构法典

关键约束确认清单：
- 后端包管理：`uv`，禁止 poetry/pipenv/conda
- 后端日志：`structlog`，禁止 `loguru`
- 后端测试：禁止 SQLite，必须用独立 PostgreSQL 测试库
- 前端状态：TanStack Query（服务端状态）+ Zustand（UI 状态），禁止 Redux
- 前端组件：默认 Server Component，仅在必要时 `'use client'`

执行 `/setup` 时，LLM 必须在输出中显式给出“配置读取回执（Config Read Receipt）”，至少包含：
- 已读取规范：`docs/BACKEND_SPEC.md`、`docs/FRONTEND_SPEC.md`、`AGENTS.md`
- 已读取 Skill：`.agents/skills/setup/SKILL.md`
- 已读取钩子：`.codex/hooks.json`（若存在）
- 未读取或不存在项（如有）

---

## 执行 SOP

### 步骤一：创建后端目录结构

```
backend/
├── pyproject.toml
├── .python-version
├── alembic.ini
├── Dockerfile
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── exceptions.py
│   │   ├── middleware.py
│   │   ├── security.py
│   │   └── observability.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── router.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   └── __init__.py
│   │   ├── value_objects/
│   │   │   └── __init__.py
│   │   ├── enums/
│   │   │   └── __init__.py
│   │   ├── errors.py
│   │   └── policies/
│   │       └── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── use_cases/
│   │   │   └── __init__.py
│   │   ├── ports/
│   │   │   ├── __init__.py
│   │   │   ├── repositories.py
│   │   │   └── external_clients.py
│   │   └── dto/
│   │       └── __init__.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   └── repositories/
│   │   │       └── __init__.py
│   │   ├── external/
│   │   │   └── __init__.py
│   │   ├── cache/
│   │   │   └── __init__.py
│   │   ├── queue/
│   │   │   ├── __init__.py
│   │   │   ├── app.py
│   │   │   ├── worker.py
│   │   │   └── tasks/
│   │   │       └── __init__.py
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   └── aliyun_oss.py
│   │   └── email/
│   │       ├── __init__.py
│   │       └── smtp_client.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── common.py
│   └── utils/
│       └── __init__.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
└── scripts/
    └── .gitkeep
```

---

### 步骤二：写入后端核心文件内容

#### `backend/pyproject.toml`

```toml
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic-settings>=2.0",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "procrastinate[aiopg]>=2.0",
    "httpx>=0.27",
    "tenacity>=8.0",
    "structlog>=24.0",
    "opentelemetry-sdk>=1.25",
    "opentelemetry-instrumentation-fastapi>=0.46b0",
    "prometheus-client>=0.20",
    "argon2-cffi>=23.1",
    "python-jose[cryptography]>=3.3",
    "uuid7>=0.1",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=5.0",
    "ruff>=0.5",
    "mypy>=1.10",
    "httpx>=0.27",
]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "alembic/*"]
```

#### `backend/.python-version`

```
3.12
```

#### `backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "myapp"  # TODO: 替换为实际项目名
    app_env: str = "local"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://myapp:changeme@localhost:5432/myapp"  # TODO: 替换为实际项目名
    database_test_url: str = "postgresql+asyncpg://myapp:changeme@localhost:5432/myapp_test"  # TODO: 替换为实际项目名
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_statement_timeout_ms: int = 30000
    db_idle_in_transaction_timeout_ms: int = 10000

    # JWT RS256
    jwt_private_key: str = ""
    jwt_public_key: str = ""
    jwt_algorithm: str = "RS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    # Aliyun OSS
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_bucket_name: str = ""
    oss_endpoint: str = ""

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    # Deployment
    app_base_path: str = ""  # 子路径部署时填入，如 /finance；独立部署留空

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Observability
    otel_exporter_endpoint: str = ""


settings = Settings()
```

#### `backend/app/core/logging.py`

```python
import logging
import sys

import structlog


def configure_logging() -> None:
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
```

#### `backend/app/core/exceptions.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__("NOT_FOUND", message, status.HTTP_404_NOT_FOUND)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__("UNAUTHORIZED", message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__("FORBIDDEN", message, status.HTTP_403_FORBIDDEN)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__("CONFLICT", message, status.HTTP_409_CONFLICT)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", details: dict | None = None) -> None:
        super().__init__("VALIDATION_ERROR", message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    from structlog import get_logger
    log = get_logger()
    log.warning(
        "app_error",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
        },
    )
```

#### `backend/app/core/middleware.py`

```python
import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: any) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            raise
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log.info(
                "request_completed",
                status_code=response.status_code if "response" in dir() else 500,
                duration_ms=duration_ms,
            )

        response.headers["X-Request-ID"] = request_id
        return response
```

#### `backend/app/core/security.py`

```python
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access",
        **(extra_claims or {}),
    }
    return jwt.encode(payload, settings.jwt_private_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
        return payload
    except JWTError as e:
        raise UnauthorizedError("Invalid or expired token") from e
```

#### `backend/app/core/observability.py`

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram, make_asgi_app
from fastapi import FastAPI
from starlette.types import ASGIApp

from app.core.config import settings

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "path"],
)


def configure_observability(app: FastAPI) -> None:
    if not settings.otel_exporter_endpoint:
        return

    resource = Resource.create({"service.name": settings.app_name, "deployment.environment": settings.app_env})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)


def get_metrics_app() -> ASGIApp:
    return make_asgi_app()  # type: ignore[return-value]
```

#### `backend/app/infrastructure/db/session.py`

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    connect_args={
        "statement_timeout": str(settings.db_statement_timeout_ms),
        "idle_in_transaction_session_timeout": str(settings.db_idle_in_transaction_timeout_ms),
    },
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

#### `backend/app/schemas/common.py`

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T
    request_id: str | None = None


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict = {}
    request_id: str | None = None


class CursorPage(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
```

#### `backend/app/api/deps.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.infrastructure.db.session import get_db

bearer_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload["sub"]
        return user_id
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db
```

#### `backend/app/api/v1/router.py`

```python
from fastapi import APIRouter

api_router = APIRouter()

# 在此注册各业务模块路由
# from app.api.v1 import users
# api_router.include_router(users.router, prefix="/users", tags=["users"])
```

#### `backend/app/infrastructure/queue/app.py`

```python
import procrastinate

from app.core.config import settings

# 从 DATABASE_URL 提取 DSN（asyncpg -> aiopg）
_dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")

App = procrastinate.App(
    connector=procrastinate.AiopgConnector(dsn=_dsn),
    import_paths=["app.infrastructure.queue.tasks"],
)
```

#### `backend/app/infrastructure/queue/worker.py`

```python
import asyncio

from app.infrastructure.queue.app import App


async def main() -> None:
    async with App.open_async():
        worker = App.worker()
        await worker.run_async()


if __name__ == "__main__":
    asyncio.run(main())
```

#### `backend/app/infrastructure/storage/aliyun_oss.py`

```python
"""阿里云 OSS 文件存储 adapter — 业务层通过 Application 端口调用，禁止直接 import。"""

import oss2

from app.core.config import settings


class AliyunOSSClient:
    def __init__(self) -> None:
        auth = oss2.Auth(settings.oss_access_key_id, settings.oss_access_key_secret)
        self.bucket = oss2.Bucket(auth, settings.oss_endpoint, settings.oss_bucket_name)

    def generate_presigned_url(self, object_key: str, expires: int = 3600) -> str:
        return self.bucket.sign_url("GET", object_key, expires)

    def put_object(self, object_key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self.bucket.put_object(object_key, data, headers={"Content-Type": content_type})
        return object_key

    def delete_object(self, object_key: str) -> None:
        self.bucket.delete_object(object_key)
```

#### `backend/app/infrastructure/email/smtp_client.py`

```python
"""SMTP 邮件发送 adapter — 邮件发送必须通过 Procrastinate 任务异步执行。"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.core.config import settings

log = structlog.get_logger()


class SMTPClient:
    def send_email(self, to: str, subject: str, html_body: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from_email
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to, msg.as_string())
            log.info("email_sent", to=to, subject=subject)
```

#### `backend/app/main.py`

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.api.v1.router import api_router

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title=f"{settings.app_name} API",
    version="0.1.0",
    root_path=settings.app_base_path,  # 子路径部署时由 APP_BASE_PATH 注入，如 /finance
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.include_router(api_router, prefix="/api/v1")
app.mount("/metrics", make_asgi_app())


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok"}
```

#### `backend/tests/conftest.py`

```python
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.infrastructure.db.session import Base, get_db
from app.main import app

test_engine = create_async_engine(settings.database_test_url, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db() -> None:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    async def override_get_db() -> AsyncSession:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

#### `backend/alembic.ini`

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
# sqlalchemy.url 由 alembic/env.py 从 settings.DATABASE_URL 动态读取，此处留空
sqlalchemy.url =

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### `backend/alembic/script.py.mako`

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

#### `backend/alembic/env.py`

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.infrastructure.db.session import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(connection=conn, target_metadata=target_metadata)
        )
        async with connection.begin():
            await connection.run_sync(lambda _: context.run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

#### `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

#### `backend/.env.example`

```env
APP_NAME=myapp
APP_ENV=local
DEBUG=true

APP_BASE_PATH=

DATABASE_URL=postgresql+asyncpg://myapp:changeme@localhost:5432/myapp
DATABASE_TEST_URL=postgresql+asyncpg://myapp:changeme@localhost:5432/myapp_test

JWT_PRIVATE_KEY=
JWT_PUBLIC_KEY=

OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
OSS_BUCKET_NAME=
OSS_ENDPOINT=

SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=

OTEL_EXPORTER_ENDPOINT=
```

---

### 步骤三：初始化后端依赖

```bash
cd backend
uv sync
```

`uv sync` 会生成 `uv.lock` 锁文件。**必须将 `uv.lock` 提交到版本库**（BACKEND_SPEC 强制要求）：

```bash
git add backend/uv.lock
```

完成后汇报：**后端脚手架已创建，等待确认后继续前端。**

---

### 步骤四：创建前端目录结构

```
frontend/
├── package.json
├── tsconfig.json
├── next.config.ts
├── eslint.config.mjs
├── .prettierrc
├── vitest.config.ts
├── playwright.config.ts
├── components.json
├── public/
└── src/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── loading.tsx
    │   ├── error.tsx
    │   ├── not-found.tsx
    │   └── globals.css
    ├── components/
    │   ├── ui/
    │   ├── shared/
    │   └── feedback/
    │       ├── EmptyState.tsx
    │       ├── ErrorState.tsx
    │       └── LoadingState.tsx
    ├── features/
    ├── lib/
    │   ├── env.ts
    │   ├── cn.ts
    │   ├── utils.ts
    │   ├── providers.tsx
    │   └── http/
    │       └── server-fetch.ts
    ├── stores/
    │   └── ui-store.ts
    └── types/
        └── index.ts
```

---

### 步骤五：写入前端核心文件内容

#### `frontend/package.json`

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint src",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:e2e": "playwright test",
    "format": "prettier --write src"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "next": "^15.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-query-devtools": "^5.0.0",
    "zustand": "^5.0.0",
    "zod": "^3.23.0",
    "react-hook-form": "^7.52.0",
    "@hookform/resolvers": "^3.9.0",
    "sonner": "^1.5.0",
    "lucide-react": "^0.400.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.4.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@types/node": "^22.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/postcss": "^4.0.0",
    "vitest": "^2.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/user-event": "^14.5.0",
    "@testing-library/jest-dom": "^6.4.0",
    "playwright": "^1.45.0",
    "@playwright/test": "^1.45.0",
    "msw": "^2.3.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.3.0",
    "prettier-plugin-tailwindcss": "^0.6.0"
  }
}
```

#### `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

#### `frontend/next.config.ts`

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  basePath: process.env.NEXT_PUBLIC_BASE_PATH ?? '',
  experimental: {
    typedRoutes: true,
  },
}

export default nextConfig
```

#### `frontend/.prettierrc`

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

#### `frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
})
```

#### `frontend/src/lib/env.ts`

```typescript
import { z } from 'zod'

const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url().default('http://localhost:8000'),
  NEXT_PUBLIC_BASE_PATH: z.string().default(''),
})

export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_BASE_PATH: process.env.NEXT_PUBLIC_BASE_PATH,
})
```

#### `frontend/src/lib/cn.ts`

```typescript
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

#### `frontend/src/lib/http/server-fetch.ts`

```typescript
import { env } from '@/lib/env'

type RequestOptions = RequestInit & {
  timeout?: number
}

export async function serverFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { timeout = 10000, ...init } = options
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const res = await fetch(`${env.NEXT_PUBLIC_API_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...init.headers,
      },
    })

    if (!res.ok) {
      const error = await res.json().catch(() => ({ message: 'Unknown error' }))
      throw new Error(error.message ?? `HTTP ${res.status}`)
    }

    return res.json() as Promise<T>
  } finally {
    clearTimeout(timeoutId)
  }
}
```

#### `frontend/src/lib/providers.tsx`

```typescript
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

#### `frontend/src/stores/ui-store.ts`

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UiStore {
  sidebarOpen: boolean
  toggleSidebar: () => void
  theme: 'light' | 'dark' | 'system'
  setTheme: (theme: 'light' | 'dark' | 'system') => void
}

export const useUiStore = create<UiStore>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      theme: 'system',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'ui-store',
      partialize: (s) => ({ sidebarOpen: s.sidebarOpen, theme: s.theme }),
    }
  )
)
```

#### `frontend/src/types/index.ts`

```typescript
export type ActionResult<T> =
  | { ok: true; data: T }
  | {
      ok: false
      message: string
      fieldErrors?: Record<string, string[]>
    }

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  request_id: string | null
}

export interface CursorPage<T> {
  items: T[]
  next_cursor: string | null
  has_more: boolean
}
```

#### `frontend/src/app/globals.css`

```css
@import "tailwindcss";

@theme {
  --font-sans: var(--font-inter), ui-sans-serif, system-ui, sans-serif;
  --font-mono: ui-monospace, monospace;
}
```

#### `frontend/src/app/layout.tsx`

```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'
import { Providers } from '@/lib/providers'
import '@/app/globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'My App',  // TODO: 替换为实际项目名
  description: 'My App Description',  // TODO: 替换为实际描述
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning className={inter.variable}>
      <body>
        <Providers>
          {children}
        </Providers>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  )
}
```

#### `frontend/src/app/page.tsx`

```typescript
export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <h1 className="text-2xl font-bold">Welcome</h1>
    </main>
  )
}
```

#### `frontend/src/app/loading.tsx`

```typescript
export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}
```

#### `frontend/src/app/error.tsx`

```typescript
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h2 className="text-xl font-semibold">出现了一些问题</h2>
      <p className="text-muted-foreground text-sm">{error.message}</p>
      <button
        onClick={reset}
        className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
      >
        重试
      </button>
    </div>
  )
}
```

#### `frontend/src/app/not-found.tsx`

```typescript
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h2 className="text-xl font-semibold">页面不存在</h2>
      <Link href="/" className="text-primary text-sm underline">
        返回首页
      </Link>
    </div>
  )
}
```

#### `frontend/src/components/feedback/EmptyState.tsx`

```typescript
interface EmptyStateProps {
  title: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <h3 className="font-semibold">{title}</h3>
      {description && <p className="text-muted-foreground text-sm">{description}</p>}
      {action}
    </div>
  )
}
```

#### `frontend/src/components/feedback/ErrorState.tsx`

```typescript
interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
}

export function ErrorState({ title = '加载失败', message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <h3 className="font-semibold text-destructive">{title}</h3>
      <p className="text-muted-foreground text-sm">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="text-primary text-sm underline">
          重试
        </button>
      )}
    </div>
  )
}
```

#### `frontend/src/components/feedback/LoadingState.tsx`

```typescript
export function LoadingState() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}
```

#### `frontend/src/test/setup.ts`

```typescript
import '@testing-library/jest-dom'
```

#### `frontend/components.json`（shadcn/ui 配置）

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/cn",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

---

### 步骤五-B：初始化前端依赖

```bash
cd frontend
pnpm install
```

`pnpm install` 会生成 `pnpm-lock.yaml` 锁文件。**必须将其提交到版本库**（前端 CI 依赖此文件做缓存）：

```bash
git add frontend/pnpm-lock.yaml
```

---

### 步骤六：创建根级 Docker Compose

#### `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-myapp}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_DB: ${POSTGRES_DB:-myapp}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-myapp}"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-myapp}:${POSTGRES_PASSWORD:-changeme}@postgres:5432/${POSTGRES_DB:-myapp}
      APP_ENV: local
      DEBUG: "true"
      APP_BASE_PATH: ${APP_BASE_PATH:-}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-myapp}:${POSTGRES_PASSWORD:-changeme}@postgres:5432/${POSTGRES_DB:-myapp}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: ["uv", "run", "python", "-m", "app.infrastructure.queue.worker"]

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_BASE_PATH: ${APP_BASE_PATH:-}
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next

volumes:
  postgres_data:
```

#### `frontend/Dockerfile`

```dockerfile
FROM node:22-alpine AS base

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 3000

CMD ["pnpm", "dev"]
```

#### `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
.venv/
venv/
dist/
*.egg-info/
.mypy_cache/
.ruff_cache/
.pytest_cache/
htmlcov/
.coverage

# Node
node_modules/
.next/
out/
dist/
.pnpm-store/

# Env
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
*.log
```

#### `.env.example`（根级）

```env
POSTGRES_USER=myapp
POSTGRES_PASSWORD=changeme
POSTGRES_DB=myapp

# 子路径部署时填入，如 /finance；独立部署留空
APP_BASE_PATH=
```

---

### 步骤七：创建 GitHub Actions CI

#### `.github/workflows/backend-ci.yml`

```yaml
name: Backend CI

on:
  push:
    paths: ["backend/**"]
  pull_request:
    paths: ["backend/**"]

jobs:
  quality:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: ai4science
          POSTGRES_PASSWORD: changeme
          POSTGRES_DB: ai4science_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Install dependencies
        run: uv sync

      - name: Lint (ruff check)
        run: uv run ruff check .

      - name: Format check (ruff format)
        run: uv run ruff format --check .

      - name: Type check (mypy)
        run: uv run mypy app tests

      - name: Test
        run: uv run pytest --cov=app --cov-report=term-missing
        env:
          DATABASE_TEST_URL: postgresql+asyncpg://ai4science:changeme@localhost:5432/ai4science_test
```

#### `.github/workflows/frontend-ci.yml`

```yaml
name: Frontend CI

on:
  push:
    paths: ["frontend/**"]
  pull_request:
    paths: ["frontend/**"]

jobs:
  quality:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: latest

      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "pnpm"
          cache-dependency-path: frontend/pnpm-lock.yaml

      - name: Install dependencies
        run: pnpm install

      - name: Type check
        run: pnpm type-check

      - name: Lint
        run: pnpm lint

      - name: Test
        run: pnpm test

      - name: Build
        run: pnpm build
```

---

### 步骤八：记录完成状态

将以下内容追加到 `CHANGELOG.md`：

```markdown
## [基建] 完成项目基础脚手架搭建

- 后端：FastAPI + uv + PostgreSQL + SQLAlchemy 2.x + Alembic + Procrastinate + structlog + JWT RS256
- 前端：Next.js 15 App Router + React 19 + TypeScript strict + Tailwind CSS 4 + shadcn/ui + TanStack Query + Zustand
- 基础设施：Docker Compose（postgres + backend + worker + frontend）
- CI/CD：GitHub Actions（后端 + 前端独立流水线）
```

清空 `SPRINT.md` 中已完成的任务，移入 `CHANGELOG.md`。

---

### 步骤九：运行验收脚本

脚手架创建完成后，运行验收脚本对所有文件和构建产物进行全面检查：

```bash
# 静态检查 + 构建检查（无需 Docker）
uv run scripts/verify_setup.py --skip-runtime

# 完整验收（含 Docker 运行时检查）
uv run scripts/verify_setup.py
```

**说明：**
- `--skip-runtime`：跳过需要 Docker 的运行时检查，适合 CI 环境或快速验证
- 不带参数：执行全部三个阶段，包括启动 Docker Compose 并验证健康端点
- 脚本退出码非 0 表示验收失败，必须修复所有 `✗` 项后重试
- `⚠ SKIP` 项为已知限制（如 Procrastinate worker、JWT 密钥），不影响验收结论

**熔断规则**：同一检查项失败超过 3 次，停止并汇报根因，不得无限重试。

---

## 质量检查清单

完成脚手架后逐项确认：

- [ ] `backend/pyproject.toml` 存在且包含所有必选依赖
- [ ] `backend/uv.lock` 已生成并提交到版本库
- [ ] `backend/app/core/config.py` 使用 `pydantic-settings`，无 `os.getenv()`
- [ ] `backend/app/core/logging.py` 使用 `structlog`，无 `loguru`
- [ ] `backend/app/core/security.py` 使用 JWT RS256 + Argon2id
- [ ] `backend/app/core/observability.py` 无裸 `any` 类型
- [ ] `backend/app/infrastructure/db/session.py` 配置所有连接池参数
- [ ] `backend/alembic/script.py.mako` 存在且内容完整
- [ ] `backend/tests/conftest.py` 使用独立 PostgreSQL 测试库 + `httpx.AsyncClient`
- [ ] `frontend/pnpm-lock.yaml` 已生成并提交到版本库
- [ ] `frontend/tsconfig.json` 开启 `strict: true`
- [ ] `frontend/src/lib/providers.tsx` 存在，包含 `QueryClientProvider`
- [ ] `frontend/src/app/layout.tsx` 无 `'use client'`，已挂载 `<Providers>`，已加载字体
- [ ] `frontend/src/app/globals.css` 无未加载的字体变量引用
- [ ] `docker-compose.yml` 包含 postgres + backend + worker + frontend 服务
- [ ] `.github/workflows/` 包含前后端 CI 流程
- [ ] `.env.example` 存在，`.env` 在 `.gitignore` 中
- [ ] `CHANGELOG.md` 已记录本次基建
- [ ] `uv run scripts/verify_setup.py --skip-runtime` 全部通过（无 `✗` 项）

---

## 下一步提示

脚手架初始化完成后，输出：

```
脚手架已就绪。

在开始开发之前，请先完成本地环境变量配置：

1. 复制后端环境变量文件：
   cp backend/.env.example backend/.env
   然后填入：APP_NAME、DATABASE_URL、DATABASE_TEST_URL、JWT_PRIVATE_KEY、JWT_PUBLIC_KEY

2. 复制前端环境变量文件：
   cp frontend/.env.local.example frontend/.env.local
   （默认值通常无需修改）

3. 启动本地数据库：
   docker compose up -d postgres

完成后告诉我这个项目要做什么，我会帮你整理需求。

示例：
  "环境变量已填好，这是一个金融分析平台，用户可以查看股票数据、分析投资组合。"
```
