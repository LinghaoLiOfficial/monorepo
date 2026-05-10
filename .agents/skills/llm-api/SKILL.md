---
description: 大模型 API（LLM API）模板化调用与结构化输出校验（Template + Schema）
---

# /llm-api Skill

## 用法

```bash
/llm-api <场景描述>
```

示例：`/llm-api 基于模板和schema生成技术术语结构化解释`

---

## 目标定位

`/llm-api` 用于将大模型调用能力（LLM Invocation）标准化为：

1. 模板渲染（Prompt Template Rendering）
2. 模型调用（Model Invocation）
3. JSON 解析（JSON Extraction）
4. Schema 校验（Schema Validation）
5. 失败重试（Retry on Parse/Validation Failure）

---

## 前置读取（必须）

执行前必须读取：

- `AGENTS.md`
- `SPRINT.md`
- `docs/BACKEND_SPEC.md`
- `.agents/skills/llm-api/SKILL.md`

并输出配置读取回执（Config Read Receipt）。

### 环境变量文件分工（必须遵守）

- `backend/.env.example`：变量模板（可提交）
- `backend/.env`：真实密钥配置（不可提交）
- 运行时只读取 `backend/.env`

---

## 执行 SOP

### 阶段 1：契约定义（Contract-First）

1. 在 `application/ports` 定义 `LLMClientPort`
2. 在 `application/services` 定义模板 + Schema 编排服务
3. 约定异常：模板格式错误、JSON解析错误、Schema校验错误

### 阶段 2：基础设施实现（Infrastructure Adapter）

1. 在 `infrastructure/external` 提供 OpenAI-compatible 客户端实现
2. 统一超时、响应格式参数
3. 输出结构化日志（structlog）

### 阶段 3：测试验证（QA）

至少覆盖：

- 模板分段解析成功/失败
- JSON 代码块提取
- Schema 校验失败
- 端到端成功路径

建议命令：

```bash
cd backend
uv run ruff check app tests
uv run pytest tests/unit/test_llm_prompt_service.py -v
```

同一错误最多重试 3 次（强熔断机制）。

---

## 自主调用策略（Auto Invocation）

当需求出现以下语义时，LLM 可自主调用 `/llm-api`，无需用户显式输入：

- “提示词模板（prompt template）”
- “结构化输出（structured output）”
- “Schema 校验（schema validation）”
- “多模型/多模板复用”

---

## 输出模板

执行后输出：

1. 修改文件列表
2. 是否需要 Alembic migration（通常否）
3. 实际验证命令
4. 风险点（模型不稳定输出、schema过严导致重试增加、超时与成本）
