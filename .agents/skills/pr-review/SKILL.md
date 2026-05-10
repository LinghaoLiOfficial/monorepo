---
description: 创建 PR 并执行代码审查清单（质量门禁 → PR 描述 → 审查要点）
---

# pr-review Skill

## 用法

```
/pr-review
```

在功能开发完成、本地测试通过后执行。

---

## 前置条件

1. 当前分支有未合并到 `main` 的提交
2. 本地质量门禁已通过（见下方步骤一）
3. `gh` CLI 已安装并已认证（`gh auth status`）

---

## 执行 SOP

### 步骤一：本地质量门禁

#### 后端（如有后端变更）

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
uv run mypy app tests
uv run pytest --cov=app --cov-report=term-missing
```

#### 前端（如有前端变更）

```bash
cd frontend
pnpm type-check
pnpm lint
pnpm test
pnpm build
```

**任何步骤失败，停止并修复后再继续。**

### 步骤二：审查 Git Diff

```bash
git diff main...HEAD --stat
git diff main...HEAD
```

逐项检查以下清单：

#### 通用检查

- [ ] 无 `.env` 文件被提交
- [ ] 无硬编码密钥、token、密码
- [ ] 无 `console.log` / `print` 调试语句遗留
- [ ] 无 `TODO` / `FIXME` 未处理（或已记录到 BACKLOG）
- [ ] Commit 信息遵循 Conventional Commits 格式

#### 后端检查

- [ ] API 路由带 `/api/v1` 版本前缀
- [ ] 所有业务 API 使用统一成功/错误响应结构
- [ ] Domain 层不依赖 Infrastructure
- [ ] API 层不直接访问 ORM 或第三方 SDK
- [ ] 新业务表主键使用 UUIDv7
- [ ] 时间字段 timezone-aware，存储 UTC
- [ ] 数据库变更有 Alembic migration
- [ ] 外部调用有 timeout、retry 和错误映射
- [ ] 权限检查覆盖对象级和租户级边界
- [ ] 单元测试和集成测试已补充

#### 前端检查

- [ ] 无裸 `any` 类型
- [ ] Server Component 未被无故改为 Client Component
- [ ] 表单包含 pending / error / success 状态
- [ ] 异步 UI 处理 Loading / Error / Empty / Success 四态
- [ ] 无敏感信息存入 localStorage 或 Zustand persist
- [ ] PC 端页面结构与核心交互已完成，移动端布局可用

### 步骤三：生成 PR 描述

根据 `git log main...HEAD` 和变更内容，生成以下格式的 PR 描述：

```markdown
## 变更摘要

<简短描述本次 PR 做了什么，为什么这样做>

## 变更内容

### 后端
- 新增 `POST /api/v1/<resource>` 接口
- 新增 `<table>` 表（migration: `xxx_<name>.py`）
- ...

### 前端
- 新增 `<Feature>` 页面（`/app/(dashboard)/<feature>/page.tsx`）
- ...

## 测试方式

```bash
# 后端
cd backend && uv run pytest tests/<feature>/ -v

# 前端
cd frontend && pnpm test

# 集成
docker compose up -d
curl http://localhost:8000/api/v1/<resource>
```

## 风险点

- ...

## 数据库变更

- [ ] 无 / 有（migration 文件：`xxx`）
- [ ] 大表迁移已分阶段设计

## Checklist

- [ ] 本地质量门禁通过
- [ ] 无敏感信息泄漏
- [ ] 测试覆盖关键路径
- [ ] CHANGELOG.md 已更新
```

### 步骤四：推送并创建 PR

```bash
# 推送当前分支
git push -u origin HEAD

# 创建 PR（使用 gh CLI）
gh pr create \
  --title "<type>(<scope>): <subject>" \
  --body "<上方生成的 PR 描述>" \
  --base main
```

### 步骤五：更新状态文件

将完成的任务从 `SPRINT.md` 移入 `CHANGELOG.md`：

```markdown
## [<type>] <功能名> — <日期>

- PR: <PR URL>
- 变更：<简短描述>
```

---

## 输出模板

完成后输出：

```
## PR 创建完成

PR URL: <url>
分支: <branch> → main

### 质量门禁结果
- [x] 后端：ruff / mypy / pytest 通过
- [x] 前端：type-check / lint / test / build 通过

### 审查清单
- [x] 无敏感信息
- [x] 测试覆盖
- [x] 状态文件已更新
```

---

## 下一步提示

PR 创建完成后，输出：

```
PR 已创建：<url>

下一步建议：
  A. 等待 CI 通过和代码审查后合并
  B. 继续开发下一个功能 → 告诉我下一个要做什么
  C. 本轮 Sprint 已完成 → 告诉我规划下一轮
```
