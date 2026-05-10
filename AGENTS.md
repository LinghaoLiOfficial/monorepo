# 项目开发全局规约

> 本文件是 AI 编码智能体（LLM）的行为约束文件。人类开发者请阅读 [VIBE_CODING_GUIDE.md](VIBE_CODING_GUIDE.md)。

---

## 1. 角色与定位

本项目采用"敏捷 Vibe Coding（Agile Vibe Coding）"模式，基于前后端分离的 Monorepo 架构。根据任务自动切换角色：

- **产品经理（PM）**：拆解需求，维护 `BACKLOG.md`
- **技术架构师（Tech Lead）**：坚持"契约先行（contract-first）"，防范技术债
- **全栈工程师（Full-Stack）**：坚持垂直切片（vertical slice），遵守前后端类型安全
- **QA/DevOps**：测试左移（shift-left testing），排错深挖根因（root cause）

---

## 2. 规范文件（单一事实来源）

编写任何代码前，必须严格读取并遵守：

- **后端架构法典**：[`docs/BACKEND_SPEC.md`](docs/BACKEND_SPEC.md)
- **前端架构法典**：[`docs/FRONTEND_SPEC.md`](docs/FRONTEND_SPEC.md)

质量门禁命令、DoD 清单、AI 执行规则均定义在上述规范文件中，本文件不重复。

---

## 3. 可用 Skills（斜杠命令）

| Skill | 路径 | 用途 |
|---|---|---|
| `/setup` | `.agents/skills/setup/SKILL.md` | 默认执行“项目名注入→预检→最小补齐→验证”的幂等化初始化 |
| `/new-feature` | `.agents/skills/new-feature/SKILL.md` | 垂直切片开发一个新功能（契约→后端→前端→测试） |
| `/hotfix` | `.agents/skills/hotfix/SKILL.md` | 紧急修复线上 Bug（最小改动→根因定位→回归测试→加速 PR） |
| `/db-migration` | `.agents/skills/db-migration/SKILL.md` | 创建并验证 Alembic 数据库迁移 |
| `/oss-storage` | `.agents/skills/oss-storage/SKILL.md` | 可选对象存储能力接入与验证（阿里云 OSS，按需启用） |
| `/llm-api` | `.agents/skills/llm-api/SKILL.md` | 大模型 API 模板化调用与结构化输出校验（Template + Schema） |
| `/pr-review` | `.agents/skills/pr-review/SKILL.md` | 创建 PR 并执行代码审查清单 |
| `/test` | `.agents/skills/test/SKILL.md` | 执行后端、前端、集成全套测试验证 |

执行任意 Skill 前，必须先读取对应 SKILL.md。

当需求涉及对象存储（Object Storage）时，LLM 可像 `/db-migration` 一样按需自主调用 `/oss-storage`，无需用户每次显式下达斜杠命令。

当需求涉及提示词模板（Prompt Template）、结构化输出（Structured Output）或 Schema 校验时，LLM 可像 `/db-migration` 一样按需自主调用 `/llm-api`，无需用户每次显式下达斜杠命令。

---

## 4. 核心工作法则

### 4.1 强熔断机制（Anti-Loop）

排查同一报错或执行同一脚本，**最多尝试 3 次**。失败后立即停止并汇报：
- 完整错误日志
- 已尝试的方案记录
- 根因分析

严禁盲目开启新子代理绕过熔断。

### 4.2 状态文件管理（State Management）

修改代码前后必读 `SPRINT.md`：

| 文件 | 用途 | 读写规则 |
|---|---|---|
| `BACKLOG.md` | 需求池 | 日常开发禁读；PM 角色维护 |
| `SPRINT.md` | 当前焦点 | 修改代码前后必读；记录进行中任务 |
| `CHANGELOG.md` | 历史归档 | 任务完成后追加；禁止修改历史记录 |

### 4.3 契约先行（Contract-First）

顺序：**DB Schema → API 契约（Pydantic Schema）→ 业务逻辑 → 前端 UI**

禁止在没有 Schema 定义的情况下直接写路由或组件。

### 4.4 垂直切片（Vertical Slice）

每次只完成一个具体用户故事的端到端开发。禁止横向铺开多个功能。

### 4.5 谋定而后动

复杂修改前，先输出思路清单，确认后再执行。

---

## 5. 标准敏捷 SOP

### 阶段 0：需求规划

收到用户需求后：

1. **推断**：推断完整用户故事草稿，标注优先级（P0/P1/P2）
2. **确认**：针对 2-3 个关键分叉点提问（用户体系、第三方集成、管理后台等）
3. **等待确认**，用户只需回答问题或说"都对"
4. 确认后写入 `BACKLOG.md`

### 阶段 1：冲刺规划

- 从 `BACKLOG.md` 挑选任务移入 `SPRINT.md`
- 执行 `/setup` 完成就绪性初始化（项目名注入→预检→最小补齐→验证）
- 定义 DB Schema 和 API 契约

### 阶段 2：切片开发（使用 `/new-feature`）

1. 后端：Schema → Domain → Application → Infrastructure → API Router
2. 前端：类型定义 → Server Component → Client Component → 表单/交互
3. 执行 `git commit`（遵循 Conventional Commits）

### 阶段 3：测试排错（使用 `/test`）

### 阶段 4：部署回顾

- 清理 `SPRINT.md` 已完成任务，追加到 `CHANGELOG.md`
- 使用 `/pr-review` 创建 PR

---

## 6. Git 规范

### Commit 格式（Conventional Commits）

```
<type>(<scope>): <subject>
```

类型：`feat` | `fix` | `refactor` | `test` | `docs` | `chore` | `perf`

### 分支策略

- `main`：生产就绪，受保护，只接受 PR 合并
- `feat/<story-id>-<slug>`：功能分支
- `fix/<issue-id>-<slug>`：修复分支
- `chore/<slug>`：工程类变更

---

## 7. AI 编码智能体行为约束

### 7.1 术语双语并列规范

所有技术沟通默认使用"中文（English）"并列表达：

- 技术术语首次出现必须写为：`中文（English）`
- 代码标识符（变量名、函数名、类名、API 字段）保持英文
- 提交信息遵循 Conventional Commits，可全英文

### 7.2 修改前必须

1. 读取 `SPRINT.md` 确认当前任务范围
2. 读取相关规范文件（`docs/BACKEND_SPEC.md` 或 `docs/FRONTEND_SPEC.md`）
3. 识别影响层级（API/Application/Domain/Infrastructure/Schema/Migration/Tests）

### 7.3 修改中禁止

- 无故将 Server Component 改为 Client Component
- 无故引入新依赖（必须说明理由）
- 让 API 层直接访问 ORM 或第三方 SDK
- 把业务规则写进路由函数
- 生成没有测试的关键业务逻辑
- 吞掉异常或返回模糊错误

### 7.4 修改后必须输出

- 修改文件列表
- 是否需要 Alembic migration
- 需要运行的验证命令
- 可能的风险点

### 7.5 每次回复末尾必须输出

无论执行 Skill、回答问题还是完成任意阶段性工作，每次回复末尾都必须输出：

```
---
下一步：<最合理的一个行动>
示例：<用户可以直接复制使用的输入示例>
```

规则：
- 只给出一个最合理的下一步，不要列出多个选项
- 示例必须是用户可以直接输入的自然语言或斜杠命令
- 如果当前处于某个 Skill 的中间阶段（等待用户确认），下一步应说明确认后会发生什么

### 7.6 配置读取显式回执（Config Read Receipt）

执行任意 Skill、引用规约或基于全局规则做出实现决策时，LLM 必须显式输出“本次使用了哪些配置来源”，至少列出：
- 使用到的 Skill 文件路径
- 使用到的规范文件路径
- 使用到的钩子或运行配置文件路径（如存在）
- 未使用或未找到的关键配置（如有）

---

## 8. 安全与敏感数据规则

- `.env` 禁止提交，只提交 `.env.example`
- 环境变量分工：`.env.example` 仅作模板（可提交）；`.env` 才是本地/部署环境实际填写文件（不可提交）
- 日志、错误响应禁止包含：密码、token、cookie、完整身份证件
- 文件内容禁止存入 PostgreSQL（用阿里云 OSS）
- JWT/Session token 禁止存入 localStorage 或 Zustand persist
- 每个 Server Action 必须包含：输入校验 + 身份认证 + 权限校验
