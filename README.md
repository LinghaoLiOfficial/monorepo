# monorepo

一个面向 AI 协作开发的全栈 Monorepo 模板，技术栈为 **FastAPI + Next.js**。
目标是让你在几分钟内完成项目初始化，并通过标准化工作流持续交付。

## 这是什么

- 适用于前后端分离的 SaaS / 管理后台 / API 服务项目
- 内置后端、前端、数据库、测试与 CI 基础规范
- 支持基于 Codex Skills 的需求拆解与垂直切片开发
- 执行框架为 Codex，底层模型可按需切换为 OpenAI / DeepSeek 等提供方

## 适合谁

- 想快速启动企业级全栈项目的个人或小团队
- 希望把"需求 → 开发 → 测试 → PR"流程标准化的团队
- 希望在开发中引入 AI 协作但保持工程约束的团队

## 3 分钟快速开始

### 前置要求

- Python 3.12+
- Node.js 22+
- Docker + Docker Compose
- uv（Python 包管理）
- pnpm（前端包管理）

### 步骤

```bash
# 1. 克隆并进入项目
git clone <your-repo-url>
cd <your-project-name>

# 2. 在 Codex 中初始化脚手架
/setup

# 3. 启动依赖服务
docker compose up -d

# 4. 启动后端
cd backend && uv sync && uv run uvicorn app.main:app --reload

# 5. 启动前端（新终端）
cd frontend && pnpm install && pnpm dev
```

验证：
- 后端健康检查：`http://localhost:8000/health`
- 前端首页：`http://localhost:3000`

## 项目结构

```text
monorepo/
├── backend/        # FastAPI 后端
├── frontend/       # Next.js 前端
├── docs/           # 架构规范文档
├── .agents/skills/ # Codex Skills
├── SPRINT.md       # 当前冲刺任务
├── BACKLOG.md      # 需求池
├── CHANGELOG.md    # 任务归档
└── README.md
```

## 技术栈

- 后端：FastAPI, SQLAlchemy, Alembic, PostgreSQL, pytest
- 前端：Next.js (App Router), React, TypeScript, Tailwind CSS
- 工程化：Docker Compose, GitHub Actions, Conventional Commits

## 文档导航

| 文档 | 用途 |
|---|---|
| [VIBE_CODING_GUIDE.md](VIBE_CODING_GUIDE.md) | 使用指南（从这里开始） |
| [AGENTS.md](AGENTS.md) | AI 智能体行为约束 |
| [docs/BACKEND_SPEC.md](docs/BACKEND_SPEC.md) | 后端架构法典 |
| [docs/FRONTEND_SPEC.md](docs/FRONTEND_SPEC.md) | 前端架构法典 |
| [SPRINT.md](SPRINT.md) | 当前冲刺任务 |
| [BACKLOG.md](BACKLOG.md) | 需求池 |
| [CHANGELOG.md](CHANGELOG.md) | 变更归档 |

## Vibe Coding 配置体系（为什么这个模板和普通模板不一样）

这套模板的核心差异不只在技术栈，而在于**配置驱动的协作开发流程**。同样是 FastAPI + Next.js，开发节奏和产出质量会因为这些 Codex 配置而显著不同。

### 1) 全局规则层（Global Rules）

- 文件：[`AGENTS.md`](AGENTS.md)
- 作用：定义 AI 智能体的角色切换、SOP、熔断规则、Git 规范、输出格式、状态文件管理方式。
- 你可以把它理解为：项目级的“团队工程约定 + 执行操作系统”。

### 2) 架构法典层（Architecture Specs）

- 文件：[`docs/BACKEND_SPEC.md`](docs/BACKEND_SPEC.md)、[`docs/FRONTEND_SPEC.md`](docs/FRONTEND_SPEC.md)
- 作用：定义后端/前端不可越界的架构边界与质量门禁（例如分层、类型安全、测试与工具链要求）。
- 你可以把它理解为：代码设计和实现时的“单一事实来源（Single Source of Truth）”。

### 3) 工作流技能层（Skills）

- 目录：`.agents/skills/*/SKILL.md`
- 已内置技能：`/setup`、`/new-feature`、`/hotfix`、`/db-migration`、`/test`、`/pr-review`
- 作用：把复杂任务拆成可重复执行的 SOP（如“新功能垂直切片开发”“紧急修复”“PR 质检”）。
- 你可以把它理解为：把“怎么做”沉淀成标准动作，减少临场发挥。

### 4) 自动钩子层（Hooks）

- 文件：[`.codex/hooks.json`](.codex/hooks.json)
- 作用：在编辑后自动执行质量动作（当前仓库中包括 Python 文件的 `ruff check --fix`，以及前端 TS/TSX 的类型检查）。
- 你可以把它理解为：低成本、即时反馈的“自动护栏”。

## 推荐阅读顺序（新人上手）

1. 先读 [`VIBE_CODING_GUIDE.md`](VIBE_CODING_GUIDE.md) 了解协作方式。
2. 再读 [`AGENTS.md`](AGENTS.md) 掌握执行规则与节奏。
3. 按职责读架构法典：后端读 [`docs/BACKEND_SPEC.md`](docs/BACKEND_SPEC.md)，前端读 [`docs/FRONTEND_SPEC.md`](docs/FRONTEND_SPEC.md)。
4. 开始开发前，选用对应 Skill 并阅读其 `SKILL.md`（例如 `/new-feature`）。

## 贡献

1. 创建分支：`git checkout -b feat/<story-id>-<slug>`
2. 完成开发与测试
3. 发起 PR，并确保 CI 全绿

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。
 
