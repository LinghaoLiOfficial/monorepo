---
description: 紧急修复线上 Bug（最小改动 → 根因定位 → 回归测试 → 加速 PR）
---

# hotfix Skill

## 用法

```
/hotfix <Bug 描述>
```

示例：`/hotfix 用户登录后 token 立即过期`

---

## 与 new-feature 的核心区别

| | `/new-feature` | `/hotfix` |
|---|---|---|
| 目标 | 交付新功能 | 最快恢复线上稳定 |
| 改动范围 | 垂直切片，可跨多层 | 最小改动，只动必要代码 |
| 需求分析 | 必须 | 跳过 |
| 契约定义 | 必须 | 仅在 API 行为变更时才需要 |
| 分支 | `feat/<slug>` | `fix/<issue-id>-<slug>` |
| PR 优先级 | 正常 | 加速，标注 `hotfix` label |

---

## 前置条件

1. 读取 `SPRINT.md`，确认当前 Sprint 状态
2. 确认 Bug 已在 `BACKLOG.md` 或 issue 中记录（如未记录，先补录）
3. 确认影响范围：是否影响数据完整性、认证、支付等高风险路径

---

## 执行 SOP

### 阶段 1：根因定位（不写代码）

输出以下内容，等待确认后继续：

```
Bug 描述：<用户报告的现象>
复现步骤：
  1. ...
根因分析：
  - 问题代码位置：<file:line>
  - 根本原因：<为什么会发生>
  - 触发条件：<什么情况下触发>
影响范围：
  - 受影响用户/数据：<估计>
  - 是否影响高风险路径（认证/支付/数据写入）：是/否
修复方案：
  - 方案：<一句话描述>
  - 改动文件：<列出>
  - 是否需要 migration：是/否
  - 是否需要数据修复脚本：是/否
风险评估：
  - 修复引入的风险：<描述>
  - 回滚方案：<如何回滚>
```

**熔断规则**：根因不明确时，禁止猜测性修复。停止并汇报已知信息。

---

### 阶段 2：创建 hotfix 分支

```bash
git checkout main
git pull origin main
git checkout -b fix/<issue-id>-<slug>
```

---

### 阶段 3：最小化修复

**核心原则：只改动修复 Bug 所必需的代码，不做任何顺手重构或优化。**

禁止在 hotfix 中：
- 重命名变量或函数
- 调整代码格式（ruff format 除外）
- 优化无关逻辑
- 引入新依赖
- 修改无关测试

#### 后端修复（如涉及）

按最小改动原则修改，改动后立即运行：

```bash
cd backend
uv run ruff check --fix <changed_file>
uv run mypy <changed_file>
```

#### 前端修复（如涉及）

按最小改动原则修改，改动后立即运行：

```bash
cd frontend
pnpm type-check
```

---

### 阶段 4：回归测试（必须）

#### 4.1 针对 Bug 写回归测试

在对应测试文件中补充一个测试，命名规范：`test_<bug_description>_regression`。

测试必须：
- 复现修复前的 Bug（注释说明）
- 验证修复后的正确行为
- 覆盖触发条件的边界情况

示例（后端）：

```python
async def test_token_expiry_regression(client: AsyncClient) -> None:
    # 修复前：登录后 token 立即过期，原因是 exp 使用了本地时间而非 UTC
    response = await client.post("/api/v1/auth/login", json={...})
    token = response.json()["data"]["access_token"]

    # 验证 token 在有效期内可用
    me_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
```

#### 4.2 运行完整测试套件

```bash
# 后端（如有后端改动）
cd backend
uv run pytest tests/ -v --tb=short

# 前端（如有前端改动）
cd frontend
pnpm test
```

**熔断规则**：同一测试失败超过 3 次，停止并汇报根因，不继续尝试。

---

### 阶段 5：数据修复（如需）

如果 Bug 导致了脏数据，必须在独立脚本中修复，禁止在迁移文件中混入数据修复逻辑：

```bash
# 脚本放在 backend/scripts/fix_<description>.py
# 执行前必须在测试库验证
uv run python scripts/fix_<description>.py --dry-run
uv run python scripts/fix_<description>.py
```

---

### 阶段 6：提交

```bash
git add <只添加必要文件，禁止 git add .>
git commit -m "fix(<scope>): <简短描述>

<根因说明>
<影响范围>
<回归测试：tests/xxx/test_xxx.py>"
```

---

### 阶段 7：加速 PR

执行质量门禁：

```bash
# 后端
cd backend && uv run ruff check . && uv run mypy app tests && uv run pytest --tb=short

# 前端
cd frontend && pnpm type-check && pnpm lint && pnpm test
```

推送并创建 PR，标注为 hotfix：

```bash
git push -u origin HEAD

gh pr create \
  --title "fix(<scope>): <简短描述>" \
  --body "<PR 描述>" \
  --base main \
  --label "hotfix"
```

PR 描述模板：

```markdown
## Bug 描述
<用户报告的现象>

## 根因
<为什么会发生，代码位置>

## 修复方案
<改动了什么，为什么这样改>

## 影响范围
- 受影响用户/数据：...
- 是否需要数据修复：是/否

## 回归测试
- 新增测试：`tests/xxx/test_xxx_regression.py`
- 测试命令：`uv run pytest tests/xxx/ -v`

## 回滚方案
<如何回滚>

## Checklist
- [ ] 根因已确认，非猜测性修复
- [ ] 改动最小化，无顺手重构
- [ ] 回归测试已补充
- [ ] 完整测试套件通过
- [ ] 数据修复脚本已执行（如需）
```

---

### 阶段 8：归档

更新 `SPRINT.md`，将 Bug 标记为已修复。

追加到 `CHANGELOG.md`：

```markdown
## [fix] <Bug 描述> — <日期>

- PR: <url>
- 根因：<一句话>
- 影响：<受影响范围>
- 回归测试：<测试文件路径>
```

---

## 输出模板

完成后输出：

```
## Hotfix 完成报告：<Bug 描述>

### 根因
<一句话>

### 修改文件
- <file:line>：<改了什么>

### 回归测试
- <tests/xxx/test_xxx_regression.py>

### 验证命令
cd backend && uv run pytest tests/<path>/ -v

### 是否需要数据修复
是/否。如是，已执行：backend/scripts/fix_<description>.py

### PR
<url>

### 风险点
- ...
```

---

## 下一步提示

Hotfix 完成后，输出：

```
Hotfix 已完成，PR 已创建。

下一步建议：
  A. 等待 PR 合并后，告诉我继续 Sprint 中的功能开发
  B. 如有脏数据需要修复，告诉我执行数据修复脚本
```
