---
description: 默认执行冲刺规划（从 BACKLOG 挑选 Ready 条目 → 写入 SPRINT → readiness 检查）
---

# /sprint-plan Skill

## 用法

```bash
/sprint-plan
```

可选示例：`/sprint-plan 本轮优先处理认证与权限相关需求`

---

## 目标定位

`/sprint-plan` 是日常开发默认入口，负责执行治理（Execution Planning），不直接写业务代码：

1. 从 `BACKLOG.md` 选择 Ready 条目
2. 执行准入检查（Entry Gate）
3. 执行 DoR（Definition of Ready）检查
4. 回写 `SPRINT.md`（含映射与范围）
5. 指定下一开发切片（通常交给 `/new-feature`）

---

## 前置读取（必须）

执行 `/sprint-plan` 前必须读取：

- `AGENTS.md`
- `BACKLOG.md`
- `SPRINT.md`
- `SYSTEM_DESIGN.md`（若存在）
- `.agents/skills/sprint-plan/SKILL.md`

按需补充读取：
- `docs/BACKEND_SPEC.md`
- `docs/FRONTEND_SPEC.md`

并在输出中给出配置读取回执（Config Read Receipt）。

---

## 强制准入检查（Entry Gate, 必须全部通过）

### Gate-1：Ready 条目存在性

`BACKLOG.md` 至少有 1 个 `Status=Ready` 条目。

### Gate-2：字段完整性

每个候选条目必须包含：
- 用户故事（User Story）
- 验收标准（Acceptance Criteria）
- 优先级（Priority）

### Gate-3：范围可执行性

候选条目必须可切成一个垂直切片（Vertical Slice），且本轮可验证。

任一 Gate 失败时：
- 立即停止 `/sprint-plan`
- 输出失败 Gate 与缺失字段
- 明确提示先执行 `/pm-plan`

---

## DoR 检查（Definition of Ready）

对拟纳入冲刺的每条需求，必须逐条勾选：

- [ ] 业务目标清晰（Business Goal Clear）
- [ ] 契约范围明确（Contract Scope Clear）
- [ ] 依赖与风险已记录（Dependencies/Risks Logged）
- [ ] 可测试性明确（Testability Defined）

规则：
- DoR 任一项不通过，不得进入本轮 Sprint
- 允许回退到 `/pm-plan` 补全后重试

---

## 回写规范（SPRINT Writeback, 必须）

`SPRINT.md` 新增或更新条目必须包含：

1. 来源 `BACKLOG.md` 条目 ID
2. 用户故事一句话摘要
3. 验收标准原文或引用
4. 本轮不做项（Out of Scope）
5. 本轮验证方式（Tests / Health Checks）

并标注：
- In Sprint（进行中）
- Deferred（延期）
- Blocked（阻塞）

---

## 熔断机制（Anti-Loop）

针对 `/sprint-plan` 的同一类准入失败（无 Ready 条目、字段缺失、DoR 不通过），最多尝试 3 次。

超过 3 次必须停止并输出：
- 完整错误日志
- 已尝试方案
- 根因分析（Root Cause Analysis）

禁止通过开启新子代理绕过熔断。

---

## 输出规范（每次 /sprint-plan 必须输出）

1. 配置读取回执（Config Read Receipt）
2. Entry Gate 检查结果（Pass/Fail）
3. DoR 检查结果（逐条）
4. 入选 Sprint 条目清单（含 BACKLOG ID）
5. `SPRINT.md` 变更摘要
6. 最高优先级风险（Top Risk）
7. 下一步建议（通常为 `/new-feature <story>`）

---

## 与流程衔接

- `/sprint-plan` 通过后，再进入 `/new-feature` 做端到端切片实现。
- 若失败且原因为需求信息不足，必须回退 `/pm-plan`。
- `/sprint-plan` 不替代 `/setup`；当环境未就绪时应先执行 `/setup`。
