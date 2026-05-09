# 当前冲刺（Sprint）

> 修改代码前后必读此文件。记录正在执行的任务。
> 完成的任务移入 `CHANGELOG.md`，不在此处保留。

---

## Sprint 1 — 项目基础脚手架

**目标：** 完成 backend/ 和 frontend/ 的基础脚手架，使项目可以本地启动。

**截止：** —

**任务列表：**

- [ ] 执行 `/setup` Skill，初始化 backend/ 和 frontend/ 目录结构
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

**任务列表：**

- [ ] 用户故事 1（使用 `/new-feature` 开发）
- [ ] 用户故事 2
- [ ] ...

**完成标准：** <可量化的验收条件>

-->
