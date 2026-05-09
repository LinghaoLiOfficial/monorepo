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

## 贡献

1. 创建分支：`git checkout -b feat/<story-id>-<slug>`
2. 完成开发与测试
3. 发起 PR，并确保 CI 全绿

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。
 
