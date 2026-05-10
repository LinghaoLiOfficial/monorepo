# 系统设计全局文档（System Design）

> 作用：作为项目全局约束（Global Constraints）与关键设计决策（Global Decisions）的单一事实来源。  
> 维护方式：由 `/global-plan` Skill 主维护；`/setup`、`/pm-plan`、`/sprint-plan`、`/new-feature` 执行前必须读取并对齐。

---

## 1. 产品愿景（Product Vision）

- 系统为何存在（Why this system exists）：待补充
- 长期目标（Long-term Goal）：待补充
- 核心价值方向（Core Value Direction）：待补充

## 2. 产品定位（Product Positioning）

### 2.1 一句话定义（One-liner）
- 待补充

### 2.2 产品边界（Product Boundaries）
- In Scope: 待补充
- Out of Scope: 待补充

### 2.3 核心价值主张（Core Value Proposition）
- 待补充

## 3. 目标用户（Target Users）

### 3.1 用户类型划分（User Segments）
- 待补充

### 3.2 典型场景与痛点（Scenarios & Pain Points）
- 待补充

### 3.3 设计重点与核心用户（Design Focus & Primary Persona）
- 待补充

## 4. 核心产品原则（Core Product Principles）

### 4.1 输入端原则（Input Principles）
- 待补充

### 4.2 处理过程原则（Processing Principles）
- 待补充

### 4.3 输出端原则（Output Principles）
- 待补充

### 4.4 长期使用原则（Long-term Use Principles）
- 待补充

### 4.5 用户控制感原则（User Control Principles）
- 待补充

## 5. 产品模块参考设计（Module Reference Design）

- 模块定位（Role of Module）：待补充
- 模块职责（Responsibilities）：待补充
- 主要能力（Capabilities）：待补充
- 模块关系（Inter-module Relationships）：待补充
- 体验重点（UX Focus）：待补充

## 6. 核心体验链路（Core Experience Journey）

- 入口链路（Entry Journey）：待补充
- 输入链路（Input Journey）：待补充
- 整理链路（Organize Journey）：待补充
- 探索链路（Explore Journey）：待补充
- 输出链路（Output Journey）：待补充
- 异常链路（Exception Journey）：待补充

## 7. 信息架构参考（Information Architecture）

- 一级导航（Primary Navigation）：待补充
- 二级导航（Secondary Navigation）：待补充
- 页面层级（Page Hierarchy）：待补充
- 高频入口（Frequent Entrances）：待补充
- 全局能力入口（Global Entrances）：待补充
- 导航形态（Navigation Patterns）：待补充

## 8. 页面清单参考（Page Inventory）

> 建议以表格维护：页面名称 | 页面目标 | 目标用户 | 核心内容 | 关键操作 | 关键状态 | 页面关系

- 待补充

## 9. 关键页面设计参考（Key Page Design）

- 页面目标（Page Goal）：待补充
- 进入原因（Entry Reason）：待补充
- 页面布局（Layout）：待补充
- 主要组件（Primary Components）：待补充
- 关键交互（Key Interactions）：待补充
- 信息优先级（Information Priority）：待补充
- 状态设计（State Design）：待补充
- 适配策略（Responsive Adaptation）：待补充

## 10. 搜索、筛选与整理体验（Search/Filter/Organize）

- 全局搜索（Global Search）：待补充
- 页面内搜索（In-page Search）：待补充
- 筛选机制（Filtering）：待补充
- 排序机制（Sorting）：待补充
- 批量整理（Bulk Operations）：待补充
- 空结果引导（Empty Results Guidance）：待补充

## 11. 智能建议与不确定性设计（AI Suggestions & Uncertainty）

- 建议呈现（Suggestion Presentation）：待补充
- 置信度表达（Confidence Expression）：待补充
- 推荐理由（Reasoning Explanation）：待补充
- 用户控制（Accept/Edit/Undo）：待补充
- 冲突提示（Conflict Prompts）：待补充
- 人工确认机制（Human Confirmation Rules）：待补充

## 12. UI 视觉方向（UI Visual Direction）

- 风格关键词（Style Keywords）：待补充
- 色彩系统（Color System）：待补充
- 字体层级（Typography Hierarchy）：待补充
- 间距与布局（Spacing/Layout Rules）：待补充
- 组件风格（Component Style）：待补充
- 图标与插画（Icons/Illustrations）：待补充

## 13. 状态设计参考（State Design Reference）

- 空状态（Empty）：待补充
- 错误状态（Error）：待补充
- 加载状态（Loading）：待补充
- 成功状态（Success）：待补充
- 权限状态（Permission）：待补充
- 危险操作状态（Dangerous Actions）：待补充

## 14. 响应式设计策略（Responsive Strategy）

- 桌面端策略（Desktop Strategy）：待补充
- 移动端策略（Mobile Strategy）：待补充
- 信息取舍（Information Trade-offs）：待补充
- 操作适配（Input Adaptation）：待补充

## 15. 产品风险与体验风险（Product & UX Risks）

- 范围风险（Scope Risk）：待补充
- 信任风险（Trust Risk）：待补充
- 复杂度风险（Complexity Risk）：待补充
- 体验干扰风险（Interruption Risk）：待补充
- 信息密度风险（Information Density Risk）：待补充
- 控制感风险（Control Risk）：待补充
- 长期使用风险（Long-term Use Risk）：待补充

## 16. 设计聚焦建议（Design Focus Recommendations）

- 核心体验闭环（Core Loop）：待补充
- 优先设计页面（Priority Pages）：待补充
- 暂不展开能力（Deferred Capabilities）：待补充
- 设计验证重点（Validation Focus）：待补充

## 17. 全局决策记录（Global Decisions / ADR Summary）

> 记录格式建议：`GD-YYYYMMDD-序号`

- Decision ID: GD-TBD
  - Topic: 待补充
  - Decision: 待补充
  - Alternatives: 待补充
  - Rationale: 待补充
  - Status: Proposed | Accepted | Deprecated

## 18. 变更记录（Change Log）

- 2026-05-10: 初始化文档模板（Initialize template）。
- 2026-05-10: 对齐 `web_system_design_prompt_working_draft` 的 16 章节结构（Align with working draft structure）。
