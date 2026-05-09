---
description: 执行后端、前端、集成全套测试验证，触发熔断机制
---

# test Skill

## 用法

```
/test [scope]
```

- `/test` — 运行全套测试（后端 + 前端 + 集成）
- `/test backend` — 仅运行后端测试
- `/test frontend` — 仅运行前端测试
- `/test integration` — 仅运行集成测试

---

## 前置条件

1. 读取 `SPRINT.md`，确认当前任务范围
2. 确认 `backend/` 和 `frontend/` 目录已存在
3. 集成测试需要 Docker 环境可用

---

## 执行 SOP

### 阶段 1：后端测试（跳过时注明）

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
uv run mypy app tests
uv run pytest --cov=app --cov-report=term-missing
```

逐条执行，任意一条失败立即停止并汇报错误。

**熔断规则**：同一错误修复尝试超过 3 次，停止并输出根因分析。

---

### 阶段 2：前端测试（跳过时注明）

```bash
cd frontend
pnpm type-check
pnpm lint
pnpm test
pnpm build
```

逐条执行，任意一条失败立即停止并汇报错误。

**熔断规则**：同一错误修复尝试超过 3 次，停止并输出根因分析。

---

### 阶段 3：集成测试（仅 `/test` 或 `/test integration`）

```bash
docker compose up -d
```

验证后端健康检查：

```bash
curl http://localhost:8000/health
```

如涉及核心业务改动，额外运行 E2E：

```bash
cd frontend
pnpm test:e2e
```

---

## 输出模板

完成后输出：

```
## 测试报告

### 后端
- ruff check：通过 / 失败（附错误）
- ruff format：通过 / 失败（附错误）
- mypy：通过 / 失败（附错误）
- pytest：通过 X 项，失败 X 项，覆盖率 XX%

### 前端
- type-check：通过 / 失败（附错误）
- lint：通过 / 失败（附错误）
- test：通过 X 项，失败 X 项
- build：通过 / 失败（附错误）

### 集成
- docker compose：正常 / 异常（附错误）
- /health：通过 / 失败
- E2E：通过 / 跳过 / 失败（附错误）

### 结论
全部通过 / 存在以下问题需修复：
- ...
```

---

## 下一步提示

测试完成后，输出：

```
测试验证完成。

下一步建议：
  A. 全部通过 → 提交 PR：/pr-review
  B. 存在失败 → 已就地修复，请确认后继续
  C. 熔断触发 → 已停止，请告诉我如何处理
```
