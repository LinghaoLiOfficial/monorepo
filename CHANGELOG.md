# Changelog

> 已完成任务的归档记录。禁止修改历史记录。
> 格式：`## [类型] 功能名 — YYYY-MM-DD`

---

## [docs] 文档结构重构，消除重复 — 2026-05-09

- 删除 AGENTS.md（与 CLAUDE.md 完全重复）
- 重写 CLAUDE.md：283 行 → 187 行，去除质量门禁命令、DoD 清单、SOP 详情等重复内容，保留 AI 核心约束
- 精简 README.md：141 行 → 93 行，去除推荐开发路径和常用命令（与 VIBE_CODING_GUIDE 重复）
- 精简 VIBE_CODING_GUIDE.md：508 行 → 458 行，删除质量门禁速查章节，架构约束速查压缩为摘要 + 引用链接
- 每个文件现在只有一个职责，规则在唯一来源中定义，其他文件通过引用指向

---

<!-- 示例：

## [基建] 完成项目基础脚手架搭建 — 2026-05-08

- 后端：FastAPI + uv + PostgreSQL + SQLAlchemy 2.x + Alembic + Procrastinate + structlog + JWT RS256
- 前端：Next.js 15 App Router + React 19 + TypeScript strict + Tailwind CSS 4 + shadcn/ui
- 基础设施：Docker Compose（postgres + backend + worker + frontend）
- CI/CD：GitHub Actions（后端 + 前端独立流水线）

## [feat] 用户注册与登录 — 2026-05-10

- PR: https://github.com/xxx/xxx/pull/1
- 后端：POST /api/v1/auth/register, POST /api/v1/auth/login
- 前端：/app/(auth)/login/page.tsx, /app/(auth)/register/page.tsx
- Migration: 001_create_users_table.py

-->
