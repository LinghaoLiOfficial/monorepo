---
description: 创建并验证 Alembic 数据库迁移（Schema 变更 → 生成 → 审查 → 验证）
---

# db-migration Skill

## 用法

```
/db-migration <迁移描述>
```

示例：`/db-migration add users table`

---

## 前置条件

1. `backend/` 目录已存在且 `uv sync` 已执行
2. PostgreSQL 本地实例已运行（`docker compose up -d postgres`）
3. SQLAlchemy 模型已在 `backend/app/infrastructure/db/models/` 中定义
4. `backend/alembic/env.py` 已正确配置（导入 `Base.metadata`）

---

## 执行 SOP

### 步骤一：确认模型变更

读取相关模型文件，确认：

- [ ] 新表主键使用 UUIDv7，字段名 `id`，类型 PostgreSQL `uuid`
- [ ] 包含 `created_at`、`updated_at`（timezone-aware，UTC）
- [ ] 使用 SQLAlchemy 2.x `Mapped` + `mapped_column` 写法
- [ ] 高频查询字段已建索引
- [ ] 唯一业务键已添加唯一约束

### 步骤二：生成迁移文件

```bash
cd backend
uv run alembic revision --autogenerate -m "<迁移描述>"
```

### 步骤三：审查生成的迁移文件

读取 `backend/alembic/versions/` 中最新生成的文件，逐项检查：

- [ ] 字段类型正确（UUID 用 `postgresql.UUID`，时间用 `TIMESTAMP(timezone=True)`）
- [ ] 索引命名规范：`ix_<table>_<column>`
- [ ] 唯一约束命名规范：`uq_<table>_<column>`
- [ ] 外键约束命名规范：`fk_<table>_<column>_<ref_table>`
- [ ] `downgrade()` 函数完整且可回滚
- [ ] 无空迁移（`upgrade()` 不为空）
- [ ] 大表迁移已分阶段设计（如有）
- [ ] 数据回填使用独立脚本或 Procrastinate 任务（如有）

如发现问题，**手动修正迁移文件**后继续。

### 步骤四：执行迁移（本地验证）

```bash
cd backend
uv run alembic upgrade head
```

验证迁移成功：

```bash
uv run alembic current
uv run alembic history --verbose
```

### 步骤五：验证回滚

```bash
cd backend
uv run alembic downgrade -1
uv run alembic upgrade head
```

确认回滚和重新升级均无报错。

### 步骤六：运行测试

```bash
cd backend
uv run pytest tests/integration/ -v -k "migration or db"
```

---

## 常见问题处理

### 自动生成检测不到变更

原因：`env.py` 未正确导入所有模型。

修复：在 `backend/alembic/env.py` 中确认：

```python
from app.infrastructure.db.session import Base
# 必须导入所有模型，触发 SQLAlchemy 注册
import app.infrastructure.db.models  # noqa: F401
```

### 迁移冲突（多分支并行开发）

```bash
cd backend
uv run alembic merge heads -m "merge migrations"
```

### 大表 ALTER 操作

对于生产环境大表（>100万行），迁移必须分阶段：

1. 阶段一：添加可空列（无锁）
2. 阶段二：后台数据回填（Procrastinate 任务）
3. 阶段三：添加 NOT NULL 约束（验证数据完整后）

---

## 输出模板

完成后输出：

```
## Migration 完成报告

### 迁移文件
backend/alembic/versions/<revision_id>_<description>.py

### 变更内容
- 新增表：...
- 修改表：...
- 新增索引：...

### 验证结果
- [x] 迁移执行成功
- [x] 回滚验证通过
- [x] 测试通过

### 风险点
- ...

### 生产部署注意事项
- ...
```

---

## 下一步提示

迁移完成后，输出：

```
Migration 已完成。

下一步建议：
  A. 继续 /new-feature 的后端实现阶段
  B. 单独验证迁移 → /test backend
```
