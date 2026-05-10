---
description: 垂直切片开发一个新功能（契约先行 → 后端 → 前端 → 测试）
---

# new-feature Skill

## 用法

```
/new-feature <功能描述>
```

示例：`/new-feature 用户注册与登录`

---

## 前置条件

1. 读取 `SPRINT.md`，确认该功能在当前 Sprint 范围内
2. 读取 `SYSTEM_DESIGN.md`（若存在），确认与全局约束一致
3. 读取 `docs/BACKEND_SPEC.md` 和 `docs/FRONTEND_SPEC.md`
4. 确认 `backend/` 和 `frontend/` 目录已存在（否则先执行 `/setup`）

---

## 执行 SOP

### 阶段 1：需求分析（PM 角色）

输出以下内容，等待确认后继续：

```
用户故事：作为 <角色>，我希望 <功能>，以便 <价值>
验收标准：
  - [ ] 条件 1
  - [ ] 条件 2
影响范围：
  - 后端：新增/修改哪些 API、表、服务
  - 前端：新增/修改哪些页面、组件
  - 数据库：是否需要 migration
```

---

### 阶段 2：契约定义（Tech Lead 角色）

#### 2.1 数据库 Schema（如需）

在 `backend/app/infrastructure/db/models/` 中定义 SQLAlchemy 模型：

```python
# 模型规范
# - 主键：UUIDv7，字段名 id，类型 PostgreSQL uuid
# - 必须包含 created_at、updated_at（timezone-aware，UTC）
# - 使用 SQLAlchemy 2.x Mapped + mapped_column 写法
```

执行 `/db-migration` 创建迁移文件。

#### 2.2 API 契约

在 `backend/app/schemas/` 中定义 Pydantic Schema：

```python
# 规范
# - 创建、更新、响应 Schema 分开定义
# - 响应 Schema 不暴露敏感字段
# - 列表接口使用 CursorPage[XxxResponse]
```

在 `backend/app/api/v1/` 中声明路由（只写签名，不写实现）：

```python
# 路由规范
# - 带 /api/v1 前缀
# - 资源命名复数名词
# - 成功响应用 SuccessResponse[T]
# - 错误响应用 ErrorResponse
```

---

### 阶段 3：后端实现（Full-Stack 角色 — 后端）

按以下顺序实现，禁止跳步：

#### 3.1 Domain 层

```
backend/app/domain/
├── entities/<feature>.py      # 业务实体（纯 Python，不依赖 SQLAlchemy）
├── value_objects/<xxx>.py     # 值对象（如有）
├── errors.py                  # 追加领域错误
└── policies/<feature>.py      # 业务规则（如有）
```

#### 3.2 Application 层

```
backend/app/application/
├── ports/repositories.py      # 追加 Repository 接口（Protocol）
├── dto/<feature>.py           # 输入/输出 DTO
└── use_cases/<feature>.py     # 用例编排（事务边界在此）
```

#### 3.3 Infrastructure 层

```
backend/app/infrastructure/db/
├── models/<feature>.py        # SQLAlchemy 模型
└── repositories/<feature>.py  # Repository 实现
```

#### 3.4 API 层

```
backend/app/api/v1/<feature>.py   # 路由实现
```

在 `backend/app/api/v1/router.py` 中注册路由。

#### 3.5 后端测试

```
backend/tests/
├── unit/<feature>/            # Domain、Application 单元测试
└── integration/<feature>/     # Repository、API 集成测试
```

运行验证：

```bash
cd backend
uv run ruff check .
uv run mypy app tests
uv run pytest tests/ -v
```

**熔断规则**：同一测试失败超过 3 次，停止并汇报。

---

### 阶段 4：前端实现（Full-Stack 角色 — 前端）

#### 4.1 类型定义

```
frontend/src/features/<feature>/
└── types.ts    # 与后端 Schema 对应的 TypeScript 类型
```

#### 4.2 Zod Schema

```
frontend/src/features/<feature>/
└── schemas.ts  # 表单校验 Schema
```

#### 4.3 数据获取（TanStack Query）

```
frontend/src/features/<feature>/
└── queries.ts  # useQuery hooks + query key factory
```

#### 4.4 数据变更（Server Action 或 TanStack Mutation）

```
frontend/src/features/<feature>/
└── actions.ts  # Server Actions（必须包含：校验 + 认证 + 权限 + revalidate）
```

#### 4.5 组件

```
frontend/src/features/<feature>/
└── components/
    ├── <Feature>List.tsx      # 列表（Server Component 优先，先完成 PC 端布局）
    ├── <Feature>Form.tsx      # 表单（Client Component，先完成 PC 端交互，再补移动端适配）
    └── <Feature>Card.tsx      # 卡片（按需，先桌面端后移动端）
```

#### 4.6 页面路由

```
frontend/src/app/(dashboard)/<feature>/
├── page.tsx        # Server Component，数据预取，先完成 PC 端页面结构
├── loading.tsx     # Suspense fallback
└── error.tsx       # 错误边界，随后补齐移动端响应式表现
```

前端实现顺序必须遵循：

1. 先设计并实现 PC 端（desktop / web）页面结构、信息层级和核心交互。
2. 再基于同一套功能与数据流补齐移动端（mobile web）响应式布局。
3. 若移动端需要偏离桌面端结构，必须说明原因并保持同一业务语义。

#### 4.7 前端验证

```bash
cd frontend
pnpm type-check
pnpm lint
pnpm test
```

---

### 阶段 5：集成验证

```bash
# 启动服务
docker compose up -d

# 验证后端
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/<resource>

# 验证前端
# 在浏览器访问 http://localhost:3000
```

---

### 阶段 6：提交与归档

```bash
git add -p
git commit -m "feat(<feature>): <简短描述>"
```

更新 `SPRINT.md`：将完成的任务标记为 `[x]`。

执行 `/pr-review` 创建 PR。

---

## 输出模板

完成后输出：

```
## 功能完成报告：<功能名>

### 修改文件
后端：
- backend/app/domain/entities/<feature>.py
- backend/app/application/use_cases/<feature>.py
- ...

前端：
- frontend/src/features/<feature>/types.ts
- ...

### 是否需要 Migration
是/否。如是，已通过 /db-migration 创建：alembic/versions/xxx_<name>.py

### 验证命令
cd backend && uv run pytest tests/<feature>/ -v
cd frontend && pnpm type-check && pnpm test

### 风险点
- ...

### 未覆盖的边界情况
- ...
```

---

## 下一步提示

功能完成后，输出：

```
功能「<功能名>」已完成。

下一步建议：
  A. 继续开发下一个功能 → 告诉我下一个要做什么
  B. 验证本次改动 → /test
  C. 提交 PR → /pr-review
```
