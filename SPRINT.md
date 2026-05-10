# 当前冲刺（Sprint）

> 修改代码前后必读此文件。记录正在执行的任务。
> 完成的任务移入 `CHANGELOG.md`，不在此处保留。
> 默认由 `/sprint-plan` 维护；仅接收来自 `BACKLOG.md` 的 Ready 条目。

---

## Sprint 1 — 项目基础脚手架

**目标：** 完成 backend/ 和 frontend/ 的基础脚手架，使项目可以本地启动。

**截止：** —

**任务列表：**

- [ ] 执行 `/setup` Skill（项目名注入→预检→最小补齐→验证），完成仓库就绪性初始化
- [ ] 验证 `docker compose up` 可以启动 postgres + backend + worker + frontend
- [ ] 验证 `GET /health` 返回 `{"status": "ok"}`
- [ ] 验证前端首页可以在浏览器访问
- [ ] 验证 GitHub Actions CI 流程配置正确

**完成标准：** 所有服务均可启动，健康检查通过，CI 绿灯。

---

<!-- Sprint 模板（新 Sprint 时复制此块）

## Sprint N — <主题>

**目标：** <本次冲刺要达成的核心目标>

**截止：** <日期>

**来源 Backlog（必填）：**
- story_id: <US-YYYYMMDD-01>
- 来源条目引用: <BACKLOG 对应条目>

**入场校验（Entry Gate）：**
- [ ] Gate-1 Ready 条目存在
- [ ] Gate-2 字段完整（User Story / Acceptance Criteria / Priority）
- [ ] Gate-3 可切分为单一垂直切片（Vertical Slice）

**DoR（Definition of Ready）：**
- [ ] 业务目标清晰（Business Goal Clear）
- [ ] 契约范围明确（Contract Scope Clear）
- [ ] 依赖与风险已记录（Dependencies/Risks Logged）
- [ ] 可测试性明确（Testability Defined）

**任务列表：**

- [ ] 用户故事 1（使用 `/new-feature` 开发）
- [ ] 用户故事 2
- [ ] ...

**验收标准（引用或原文）：**
- [ ] <来自 BACKLOG 的 AC-1>
- [ ] <来自 BACKLOG 的 AC-2>

**本轮不做项（Out of Scope）：**
- <明确不在本轮实现的内容>

**状态跟踪（每条故事至少一个状态）：**
- In Sprint（进行中）| Deferred（延期）| Blocked（阻塞）| Done（完成）

**验证方式（Tests / Health Checks）：**
- `uv run pytest ...`
- `pnpm test`
- `curl http://localhost:8000/health`

**完成标准：** <可量化的验收条件>

-->
