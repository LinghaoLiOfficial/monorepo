---
description: 默认执行“项目名注入→预检→最小补齐→验证”的幂等化初始化流程（FastAPI 后端 + Next.js 前端）
---

# /setup Skill

## 目标定位

`/setup` 的唯一默认模式是：

1. 项目名注入（Project Name Injection）
2. 预检（Preflight）
3. 对齐补齐（Reconcile）
4. 验证（Verify）

该流程必须满足：

- 幂等执行（Idempotent）：重复执行不应破坏已有项目。
- 最小补齐（Minimal Reconciliation）：只创建缺失项，不覆盖已有业务实现。
- 契约先行（Contract-First）：优先补齐配置/Schema骨架，再涉及路由与页面。

---

## 前置读取（必须）

执行 `/setup` 前必须读取：

- `AGENTS.md`
- `docs/BACKEND_SPEC.md`
- `docs/FRONTEND_SPEC.md`
- `.agents/skills/setup/SKILL.md`
- `.codex/hooks.json`（若存在）

并在输出中给出配置读取回执（Config Read Receipt）。

---

## 阶段 0：项目名注入（Project Name Injection）

### 0.1 必须询问并确认

执行 `/setup` 时，必须先询问用户目标项目名（`project_name`）。

### 0.2 占位符替换范围

默认将仓库中的 `myapp` 占位符替换为 `project_name`，至少覆盖：

- 根目录 `.env.example`
- `docker-compose.yml`
- `backend/.env.example`
- `backend/alembic.ini`
- `backend/app/core/config.py`

### 0.3 替换约束

- 仅替换模板占位符 `myapp`，不得改动其他业务标识符。
- 若目标文件不存在，记录为 `WARN`，继续后续阶段。
- 若替换后检测到 URL/路径不合法，标记为 `FAIL` 并停止。

---

## 阶段 A：预检（Preflight）

### A1. 工具链检查

必须检查以下工具可用性与版本约束：

- Python >= 3.12
- `uv`
- Node.js >= 22
- `pnpm`
- Docker + Docker Compose

### A2. 仓库结构检查

检查并报告以下关键路径是否存在：

- `backend/`
- `frontend/`
- `docker-compose.yml`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- 根目录 `.env.example`

### A3. 预检结果分级

预检结果必须按以下级别输出：

- `PASS`：满足要求
- `WARN`：非阻断差异，可在补齐阶段处理
- `FAIL`：阻断问题（例如关键工具缺失），必须停止并报告

---

## 阶段 B：对齐补齐（Reconcile）

### B1. 允许操作

- 创建缺失目录与缺失文件
- 补齐规范要求的最小模板占位（如 `__init__.py`、`.gitkeep`）
- 补齐 `.env.example` 中规范要求但缺失的键

### B2. 禁止操作

- 禁止覆盖已有非空文件
- 禁止重写项目特定配置值
- 禁止注入完整业务示例
- 禁止绕过规范新增不必要中间件/依赖

### B3. 冲突策略

若目标文件已存在且内容与模板不一致：

- 仅记录为“冲突（Conflict）”
- 不自动改写
- 在 `/setup` 报告中提示后续人工决策

---

## 阶段 C：验证（Verify）

### C1. 静态验证

建议执行：

- `uv run scripts/verify_setup.py --skip-runtime`

### C2. 运行时验证（可用 Docker 时）

建议执行：

- `uv run scripts/verify_setup.py`

### C3. 最小健康检查

至少确认：

- `GET /health` 可访问
- 前端首页可访问

---

## 输出规范（每次 /setup 必须输出）

1. 配置读取回执（Config Read Receipt）
2. 项目名注入结果（替换文件与替换计数）
3. 预检报告（PASS/WARN/FAIL）
4. 补齐清单（新增目录/文件）
5. 冲突清单（如有）
6. 是否需要 Alembic migration（是/否 + 原因）
7. 实际执行的验证命令
8. 最高优先级风险（Top Risk）

---

## 与规范的一致性声明

- 脚手架能力边界与禁止项以 `docs/BACKEND_SPEC.md` 与 `docs/FRONTEND_SPEC.md` 为准。
- 具体 `/setup` 执行流程以本 Skill 为单一事实来源。
