# Vibe Coding 使用指南

> 本指南说明如何基于此模板，用 Claude Code 开发一个全新的 Web 全栈项目。

---

## 一、什么是 Vibe Coding 模式

本模板采用"敏捷 Vibe Coding"模式：你负责**决策**，Claude Code 负责**执行**。

核心流程：
1. 你描述需求 → LLM assistant 拆解为用户故事
2. 你确认方案 → LLM assistant 按契约先行顺序实现
3. 你验收结果 → LLM assistant 运行质量门禁并归档

Claude Code 会自动切换角色（PM / Tech Lead / Full-Stack / QA）模式，你只需要用自然语言沟通。

---

## 二、开始一个新项目

### 第一步：复制模板到新项目

```bash
# 方式一：使用 GitHub Template（推荐）
# 在 GitHub 页面点击 "Use this template" → "Create a new repository"

# 方式二：手动复制
cp -r monorepo my-new-project
cd my-new-project
git init
git add .
git commit -m "chore: initial project scaffold"
git remote add origin <your-repo-url>
```

### 第二步：用 Claude Code 打开项目

```bash
cd my-new-project
claude
```

### 第三步：初始化脚手架

在 Claude Code 中执行：

```
/setup
```

LLM assistant 会询问项目名称，然后初始化 `backend/` 和 `frontend/` 目录，并将所有 `myapp` 占位符替换为你的项目名。

### 第四步：描述你的项目需求

脚手架就绪后，告诉 LLM assistant 你要做什么：

```
这是一个任务管理 SaaS 平台，用户可以创建项目、分配任务、追踪进度。
```

LLM assistant 会将需求拆解为用户故事，确认后自动写入需求池。

---

## 三、日常开发流程

### 3.1 规划需求（PM 角色）

直接告诉 LLM assistant 你的需求，不需要精心构思：

```
我要做一个电商平台。
```

LLM assistant 会先推断出完整的功能模块草稿，然后针对 2-3 个关键细节向你确认：

```
根据你的描述，我推断这个平台包含：
- [P0] 用户注册与登录
- [P0] 商品浏览与搜索
- [P0] 购物车与下单
- [P1] 支付集成
- [P1] 订单管理
- [P2] 管理后台

有几个细节需要确认：
1. 支付渠道用支付宝/微信支付，还是其他？
2. 是否需要独立的商家管理后台？
3. 商品是单一规格还是支持多规格（颜色、尺码）？
```

你只需要回答问题，或者说"都对"，LLM assistant 会自动整理并归档需求。

### 3.2 冲刺规划

告诉 LLM assistant 本轮想做哪些功能：

```
本轮先做用户注册和登录。
```

或者让 LLM assistant 根据优先级自动建议：

```
请帮我进行本次规划。
```

LLM assistant 会从 BACKLOG 中挑选合适的任务，确认范围后自动更新 SPRINT.md。

### 3.3 开发新功能（核心流程）

使用 `/new-feature` Skill：

```
/new-feature 用户注册与邮箱验证
```

LLM assistant 会按以下顺序自动执行，**每个阶段完成后等待你确认再继续**：

**阶段 1：需求分析**
- 输出用户故事、验收标准、影响范围
- 你确认后继续

**阶段 2：契约定义**
- 定义数据库 Schema（SQLAlchemy 模型）
- 定义 API 契约（Pydantic Schema + 路由签名）
- 你审查后继续

**阶段 3：后端实现**
- Domain 层（业务实体、规则）
- Application 层（用例编排）
- Infrastructure 层（DB Repository）
- API 层（路由实现）
- 运行 ruff + mypy + pytest

**阶段 4：前端实现**
- TypeScript 类型定义
- Zod 表单校验 Schema
- TanStack Query hooks
- Server Actions
- 组件（列表、表单、卡片）
- 页面路由（含 loading/error 状态）
- 运行 type-check + lint + test

**阶段 5：集成验证**
- `docker compose up -d` 启动服务
- 验证 API 端点
- 验证前端页面

### 3.4 数据库迁移

每次修改数据库 Schema 后：

```
/db-migration add users table
```

LLM assistant 会：
1. 生成 Alembic 迁移文件
2. 审查迁移内容（字段类型、索引、约束命名）
3. 执行迁移并验证回滚

### 3.5 紧急修复

```
/hotfix 用户登录后 token 立即过期
```

LLM assistant 会：
1. 先定位根因（不写代码），输出分析报告等你确认
2. 最小化修复（只改必要代码）
3. 补充回归测试
4. 运行完整测试套件

### 3.6 测试验证

```
/test              # 全套（后端 + 前端 + 集成）
/test backend      # 仅后端
/test frontend     # 仅前端
/test integration  # 仅集成
```

LLM assistant 会逐条运行质量门禁命令，任意一条失败立即停止并汇报错误。同一错误最多尝试修复 3 次，超过后触发熔断机制。

### 3.7 创建 PR

```
/pr-review
```

LLM assistant 会：
1. 运行所有质量门禁（lint + type-check + test + build）
2. 审查 Git Diff（安全检查 + 规范检查）
3. 生成 PR 描述
4. 推送并用 `gh` CLI 创建 PR

> 前置要求：远程仓库已配置（`git remote add origin <url>`）且 `gh` CLI 已认证（`gh auth login`）

---

## 四、与 LLM assistant 沟通的技巧

### 术语表达建议（中英文并列）

为减少理解偏差，建议在技术术语首次出现时使用“中文（English）”格式。例如：

- 首屏区（hero section）
- 轮播图（carousel）
- 横幅（banner）
- 断点（breakpoint）
- 悬停态（hover state）
- 接口契约（API contract）

推荐你直接用中文描述需求；LLM assistant 会按本项目规范输出双语术语，确保可读性与准确性。

### 给出足够上下文

```
# 好的方式
我要实现订单支付功能。用户选好商品后点击支付，
跳转到支付宝支付页面，支付成功后更新订单状态并发送确认邮件。
注意：订单金额需要在后端二次校验，不能信任前端传来的价格。

# 不够好的方式
做一个支付功能
```

### 在关键节点确认

LLM assistant 在每个阶段结束后会等待你确认。不要跳过这些确认点——它们是你把控方向的机会：

- 需求分析完成后：确认用户故事和验收标准是否准确
- 契约定义完成后：确认 API 设计是否合理
- 后端实现完成后：确认测试是否覆盖关键路径

### 遇到问题时

如果 LLM assistant 卡住了（同一错误尝试超过 3 次），它会触发熔断机制并汇报：

```
已尝试 3 次，均失败。
根因分析：...
已尝试方案：...
建议下一步：...
```

这时你可以：
- 提供更多上下文（错误日志、环境信息）
- 指定一个不同的解决方向
- 手动解决后让 LLM assistant 继续

### 调整架构决策

如果你想偏离默认架构（比如不用 Procrastinate，改用 Celery），直接告诉 LLM assistant：

```
这个项目不需要任务队列，请在 setup 时跳过 Procrastinate 相关配置。
```

LLM assistant 会相应调整，但会提示你这偏离了 BACKEND_SPEC 的默认规范。

---

## 五、状态文件管理

三个文件各司其职，LLM assistant 会自动维护：

| 文件 | 用途 | 你需要做什么 |
|---|---|---|
| `BACKLOG.md` | 需求池 | 描述需求，LLM assistant 帮你写入 |
| `SPRINT.md` | 当前冲刺 | 每次开发前确认任务范围 |
| `CHANGELOG.md` | 完成归档 | 任务完成后 LLM assistant 自动追加 |

**重要**：每次开始新的开发会话时，先让 LLM assistant 同步当前状态：

```
我们继续上次的开发，请告诉我当前冲刺的进度。
```

---

## 六、架构约束速查

> 完整规范见 [docs/BACKEND_SPEC.md](docs/BACKEND_SPEC.md) 和 [docs/FRONTEND_SPEC.md](docs/FRONTEND_SPEC.md)。

开发时 LLM assistant 会自动遵守这些约束，但你也需要了解关键禁止项：

**后端**：禁止 API 层直接访问 ORM / 第三方 SDK；禁止业务规则写进路由；禁止 Domain 依赖 Infrastructure；禁止 SQLite（测试也用 PostgreSQL）；禁止 Redis（缓存/限流/锁用 PostgreSQL）

**前端**：禁止无故将 Server Component 改为 Client Component；禁止 JWT/token 存入 localStorage；禁止 Redux；禁止裸 `any`

**必须做**：API 带 `/api/v1` 前缀；新业务表主键用 UUIDv7；时间字段存 UTC 输出 ISO 8601；列表接口用 cursor pagination；每个 Server Action 包含校验 + 认证 + 权限

---

## 七、常见场景示例

### 场景 A：从零开始一个 SaaS 项目

```
# 第一次打开项目
1. /setup（初始化脚手架）
2. 描述项目背景和核心功能，LLM assistant 自动整理需求
3. 告诉 LLM assistant 本轮要做哪些功能
4. /new-feature 用户注册与登录
5. /test（验证通过后继续）
6. /new-feature 核心业务功能 A
7. /test
8. /pr-review
```

### 场景 B：在已有项目上加新功能

```
# 已有 backend/ 和 frontend/
1. 告诉 LLM assistant 继续上次的开发，确认当前进度
2. 描述新需求，LLM assistant 自动整理并归档
3. 告诉 LLM assistant 本轮要做哪个功能
4. /new-feature <新功能>
5. /test
6. /pr-review
```

### 场景 C：修复线上 Bug

```
# 收到 Bug 报告
1. /hotfix <Bug 描述>
2. 确认根因分析报告
3. 确认修复方案
4. LLM assistant 执行修复 + 回归测试
5. /test backend（快速验证）
6. /pr-review（标注 hotfix label）
```

### 场景 D：数据库 Schema 变更

```
# 需要新增字段或表
1. /new-feature 包含 Schema 变更的功能
   （LLM assistant 会在阶段 2 自动调用 /db-migration）

# 或单独执行迁移
2. /db-migration add column email_verified to users
```

---

## 八、项目定制化

### 修改项目名称

`/setup` 执行时 LLM assistant 会提示你输入项目名，它会自动替换所有 `myapp` 占位符。

如果已经 setup 完成后想改名，告诉 LLM assistant：

### 子路径部署（整合到个人网站）

如果这个项目需要作为个人网站的一个子模块部署（如 `yoursite.com/finance`），在根目录 `.env` 中填入：

```env
APP_BASE_PATH=/finance
```

留空则以根路径独立部署，行为与默认完全一致。

`APP_BASE_PATH` 会自动传递给：
- 后端：FastAPI 的 `root_path`，影响 OpenAPI 文档和重定向路径
- 前端：Next.js 的 `basePath`，影响所有页面路由和静态资源路径

> 注意：修改 `APP_BASE_PATH` 后前端需要重新构建（`pnpm build`），因为 `basePath` 在构建时确定。

```
请将项目名从 myapp 全局替换为 taskflow，
包括 config.py、.env.example、docker-compose.yml、alembic.ini。
```

### 调整技术选型

在 `/setup` 之前告诉 LLM assistant 你的定制需求：

```
setup 时请注意：
- 不需要 Procrastinate 任务队列（这个项目没有异步任务）
- 不需要阿里云 OSS（用本地文件存储即可）
- SMTP 邮件服务改用 SendGrid API
```

### 添加新的 Skill

如果你有重复性的工作流，可以让 LLM assistant 帮你创建新的 Skill：

```
请帮我创建一个 /seed-data Skill，
用于在开发环境快速插入测试数据。
```

---

## 九、故障排查

### LLM assistant 不遵守架构规范

检查 `CLAUDE.md` 是否在项目根目录，Claude Code 会自动加载它。

如果 LLM assistant 偏离了规范，直接指出：

```
你刚才在 API 层直接调用了 ORM，这违反了 BACKEND_SPEC 的分层规范。
请按照 Domain → Application → Infrastructure → API 的顺序重新实现。
```

### Hooks 不生效

检查 `.claude/settings.json` 中的 hooks 配置。hooks 依赖 `git` 命令获取仓库根目录，确保项目是 git 仓库：

```bash
git status  # 确认在 git 仓库中
```

### 质量门禁失败

```bash
# 后端：查看详细错误
cd backend && uv run ruff check . --show-source
cd backend && uv run mypy app tests --show-error-codes

# 前端：查看详细错误
cd frontend && pnpm type-check 2>&1 | head -50
cd frontend && pnpm lint --max-warnings 0
```

### Docker 服务启动失败

```bash
# 查看日志
docker compose logs postgres
docker compose logs backend

# 重建镜像
docker compose build --no-cache backend
docker compose up -d
```

---

## 十、参考文档

| 文档 | 用途 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | 全局开发规约（LLM assistant 自动读取） |
| [docs/BACKEND_SPEC.md](docs/BACKEND_SPEC.md) | 后端架构法典（20 节详细规范） |
| [docs/FRONTEND_SPEC.md](docs/FRONTEND_SPEC.md) | 前端架构法典（20 节详细规范） |
| [SPRINT.md](SPRINT.md) | 当前冲刺任务 |
| [BACKLOG.md](BACKLOG.md) | 需求池 |
| [CHANGELOG.md](CHANGELOG.md) | 完成任务归档 |
