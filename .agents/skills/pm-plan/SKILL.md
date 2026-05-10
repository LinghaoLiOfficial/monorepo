---
description: 按需执行需求规划（用户故事草拟 → 关键分叉确认 → 写入 BACKLOG）
---

# /pm-plan Skill

## 用法

```bash
/pm-plan <需求描述>
```

示例：`/pm-plan 我们要新增团队成员邀请与角色管理`

---

## 目标定位

`/pm-plan` 只负责需求规划（Demand Planning），不进入开发实现：

1. 推断完整用户故事草稿（User Story Draft）
2. 标注优先级（Priority）
3. 提出 2-3 个关键分叉确认问题（Decision Branches）
4. 用户确认后写入 `BACKLOG.md`

适用场景：
- `BACKLOG.md` 中无 Ready 条目
- 现有条目缺少用户故事（User Story）或验收标准（Acceptance Criteria）
- 新需求尚未完成结构化澄清

---

## 前置读取（必须）

执行 `/pm-plan` 前必须读取：

- `AGENTS.md`
- `SPRINT.md`
- `BACKLOG.md`
- `SYSTEM_DESIGN.md`（若存在）
- `.agents/skills/pm-plan/SKILL.md`

若需要评估技术影响，再补充读取：
- `docs/BACKEND_SPEC.md`
- `docs/FRONTEND_SPEC.md`

并在输出中给出配置读取回执（Config Read Receipt）。

---

## 执行 SOP

### 阶段 1：需求草拟（Draft）

基于用户输入，输出标准化草稿：

```text
用户故事（User Story）：作为 <角色>，我希望 <目标>，以便 <价值>
优先级（Priority）：P0 | P1 | P2
验收标准（Acceptance Criteria）：
- [ ] 条件 1
- [ ] 条件 2
边界范围（In Scope）：
- 本轮包含项
非本轮范围（Out of Scope）：
- 本轮不做项
```

要求：
- 首次输出必须覆盖上述 5 块内容
- 禁止直接进入代码实现

### 阶段 2：关键分叉确认（Decision Confirm）

必须提出 2-3 个关键问题，优先围绕：
- 用户体系（鉴权/权限）
- 第三方集成（支付/消息/存储）
- 管理后台与运营规则

等待用户确认（例如：逐条回答、或“都对”）后再继续。

### 阶段 3：回写需求池（Backlog Writeback）

确认后写入 `BACKLOG.md`，每条新增需求至少包含：
- `story_id`（唯一标识，建议 `US-YYYYMMDD-序号`）
- 用户故事（User Story）
- 优先级（Priority）
- 验收标准（Acceptance Criteria）
- 状态（Status）：`Draft` 或 `Ready`

Ready 判定规则（Definition of Ready for Backlog）：
- 用户故事完整
- 验收标准至少 2 条
- 分叉决策已确认
- 关键依赖与风险已记录

若满足上述条件，状态写为 `Ready`；否则写为 `Draft` 并记录缺口。

---

## 风险防护（必须）

### 1) 防上下文丢失（Context Loss Prevention）

写入 `BACKLOG.md` 时，必须保留：
- 用户原始意图一句话摘要
- 核心业务价值
- 非目标范围（Out of Scope）

### 2) 防重复规划（Duplicate Planning Prevention）

回写前必须检查是否存在语义重复条目：
- 若重复，更新现有条目状态/字段，不新增重复项
- 若不确定是否重复，标注 `NEEDS-REVIEW` 并提示人工确认

### 3) 强熔断（Anti-Loop）

同一规划阻塞问题（例如信息缺失导致无法判定优先级）最多重试 3 次。超过 3 次必须停止并输出：
- 完整错误信息
- 已尝试澄清记录
- 根因分析（Root Cause Analysis）

---

## 输出规范（每次 /pm-plan 必须输出）

1. 配置读取回执（Config Read Receipt）
2. 用户故事草稿
3. 关键分叉问题（2-3 条）
4. 是否已获得确认
5. `BACKLOG.md` 变更摘要（新增/更新条目）
6. 最高优先级风险（Top Risk）
7. 下一步建议（通常为 `/sprint-plan` 或补充确认）

---

## 与流程衔接

- `/pm-plan` 完成后，不自动进入开发。
- 后续应执行 `/sprint-plan` 将 Ready 条目纳入 `SPRINT.md`。
- 若 `/pm-plan` 产出仍为 `Draft`，先补齐缺口再进入 `/sprint-plan`。
