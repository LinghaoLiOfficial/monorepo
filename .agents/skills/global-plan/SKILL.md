---
description: 执行全局需求规划（系统设计意图采集 → 关键架构分叉确认 → 写入 SYSTEM_DESIGN）
---

# /global-plan Skill

## 用法

```bash
/global-plan <全局目标或系统设计思路>
```

示例：`/global-plan 我们要做 B2B SaaS，多租户隔离，首期支持邮箱登录与阿里云 OSS`

---

## 目标定位

`/global-plan` 只负责全局规划（Global Planning），不进入功能开发实现：

1. 采集系统设计全局性思路（Global Design Intent）
2. 输出关键架构分叉（Architecture Decision Branches）
3. 形成长期约束与假设（Constraints & Assumptions）
4. 写入并维护 `SYSTEM_DESIGN.md`

职责边界：
- `/global-plan` 负责“为什么做（Why）+ 边界与原则（Boundaries/Principles）”
- `/pm-plan` 负责“做什么需求（What in Backlog）”
- `/sprint-plan` 负责“本轮做哪项（What Now）”

---

## 前置读取（必须）

执行 `/global-plan` 前必须读取：

- `AGENTS.md`
- `SPRINT.md`
- `SYSTEM_DESIGN.md`（若不存在则初始化）
- `.agents/skills/global-plan/SKILL.md`

并必须先确认：
- `/setup` 已执行完成（环境已就绪）。若未完成，先执行 `/setup`，再继续 `/global-plan`。

若需评估技术可行性，再补充读取：
- `docs/BACKEND_SPEC.md`
- `docs/FRONTEND_SPEC.md`

并在输出中给出配置读取回执（Config Read Receipt）。

---

## 执行 SOP

### 阶段 1：全局意图草拟（Global Intent Draft）

基于用户输入，先输出结构化草稿（建议按以下章节）：

```text
1) 产品愿景（Vision）
2) 产品定位（Positioning）
3) 目标用户（Target Users）
4) 核心产品原则（Product Principles）
5) 产品模块参考设计（Module Design）
6) 核心体验链路（Core Journey）
7) 信息架构（Information Architecture）
8) 页面清单（Page Inventory）
9) 关键页面设计（Key Page Design）
10) 搜索/筛选/整理体验（Findability & Organization）
11) 智能建议与不确定性设计（AI/Uncertainty Design）
12) UI 视觉方向（Visual Direction）
13) 状态设计（State Design）
14) 响应式策略（Responsive Strategy）
15) 产品与体验风险（Product/UX Risks）
16) 设计聚焦建议（Design Focus）
```

### 阶段 2：关键分叉确认（Decision Confirm）

必须提出 2-3 个关键问题，优先围绕：
- 租户与数据隔离（Tenant/Data Isolation）
- 鉴权与权限（AuthN/AuthZ）
- 外部集成与存储策略（Integration/Storage）

等待用户确认（逐条回答或“都对”）后再继续。

### 阶段 3：全局文档回写（System Design Writeback）

确认后更新 `SYSTEM_DESIGN.md`，优先按 16 章节完整回写；若信息不足，至少保证：
- 愿景/定位/用户/边界
- 核心体验链路与信息架构
- 关键页面与状态策略
- 风险与设计聚焦建议
- 全局决策记录与版本变更记录

同一决策需保留历史，禁止覆盖式丢失上下文。

---

## 治理规则（必须）

### 1) 长期背景生效（Persistent Context）

`SYSTEM_DESIGN.md` 作为全局背景信息文件，后续执行：
- `/setup`
- `/pm-plan`
- `/sprint-plan`
- `/new-feature`

时，必须优先读取并对齐其中的全局约束。

### 2) 防重复与防冲突（Duplicate/Conflict Prevention）

写入前检查是否存在语义重复决策：
- 若重复，更新原决策状态，不新增重复项
- 若冲突，新增“冲突决策记录（Conflict Record）”并标注 `NEEDS-REVIEW`

### 3) 强熔断（Anti-Loop）

同一信息缺失或冲突问题最多重试 3 次。超过 3 次必须停止并输出：
- 完整错误信息
- 已尝试澄清记录
- 根因分析（Root Cause Analysis）

---

## 输出规范（每次 /global-plan 必须输出）

1. 配置读取回执（Config Read Receipt）
2. 全局意图草稿
3. 关键分叉问题（2-3 条）
4. 是否已获得确认
5. `SYSTEM_DESIGN.md` 变更摘要（新增/更新章节）
6. 最高优先级风险（Top Risk）
7. 下一步建议（通常为 `/pm-plan` 或 `/sprint-plan`）

---

## 与流程衔接

- `/global-plan` 完成后，不自动进入开发。
- `/global-plan` 必须在 `/setup` 之后执行，不得前置替代环境初始化。
- 新需求先更新全局约束，再进入 `/pm-plan` 细化需求。
- 当全局设计无变更时，可跳过 `/global-plan`，直接进入 `/pm-plan` 或 `/sprint-plan`。
