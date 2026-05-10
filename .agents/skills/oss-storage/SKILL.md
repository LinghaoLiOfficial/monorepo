---
description: 可选对象存储能力（阿里云 OSS）接入与验证（按需启用，不污染默认模板）
---

# /oss-storage Skill

## 用法

```bash
/oss-storage <场景描述>
```

示例：`/oss-storage 为用户头像上传增加 OSS 存储`

---

## 目标定位

`/oss-storage` 用于把对象存储（Object Storage）作为“可选能力（Optional Capability）”接入项目。

原则：

1. 默认关闭（`OSS_ENABLED=false`）
2. 契约先行（Contract-First）：先定义应用层端口（Application Port）再接入基础设施（Infrastructure Adapter）
3. 垂直切片（Vertical Slice）：仅覆盖一个用户故事的存储链路

---

## 前置读取（必须）

执行前必须读取：

- `AGENTS.md`
- `SPRINT.md`
- `docs/BACKEND_SPEC.md`
- `.agents/skills/oss-storage/SKILL.md`

并输出配置读取回执（Config Read Receipt）。

### 环境变量文件分工（必须遵守）

- `backend/.env.example`：OSS 配置模板（可提交），用于提供变量清单。
- `backend/.env`：OSS 真实配置（不可提交），需填写 `OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET` 等真实值。
- 应用运行读取的是 `backend/.env`；仅在新增/调整变量定义时更新 `backend/.env.example`。

---

## 执行 SOP

### 阶段 1：契约定义（Tech Lead）

1. 在 `backend/app/application/ports/external_clients.py` 定义 `ObjectStorageClient` 协议
2. 明确方法契约：`save/load/load_stream/delete/exists/list_files`
3. 约定异常语义：
   - `ObjectStorageError`：存储调用失败
   - `ObjectTooLargeError`：超过内存加载上限

### 阶段 2：基础设施实现（Full-Stack 后端）

1. 在 `backend/app/infrastructure/storage/aliyun_oss.py` 实现 `AliyunOssStorage`
2. 使用 `asyncio.to_thread` 包装同步 SDK，避免阻塞 async 链路
3. 使用 `structlog` 输出结构化日志
4. 提供 `get_aliyun_oss_storage()` 工厂，未启用时快速失败

### 阶段 3：配置接入（Config）

在 `backend/app/core/config.py` 与 `backend/.env.example` 增加：

- `OSS_ENABLED`
- `OSS_ACCESS_KEY_ID`
- `OSS_ACCESS_KEY_SECRET`
- `OSS_BUCKET`
- `OSS_REGION`
- `OSS_ENDPOINT`
- `OSS_MAX_CONNECTIONS`
- `OSS_DISABLE_SSL`
- `OSS_USE_CNAME`
- `OSS_LOAD_MAX_SIZE`

### 阶段 4：测试验证（QA）

至少补充：

- `load` 成功路径
- `load` 大文件熔断（`ObjectTooLargeError`）

建议命令：

```bash
cd backend
uv run ruff check app tests
uv run pytest tests/unit/test_aliyun_oss_storage.py -v
```

同一错误最多重试 3 次（强熔断机制）。

---

## 新项目复用步骤

1. 复制下列文件到新项目同等层级：
   - `backend/app/application/ports/external_clients.py`（含 `ObjectStorageClient`）
   - `backend/app/infrastructure/storage/aliyun_oss.py`
   - `backend/app/infrastructure/storage/__init__.py`
   - `backend/tests/unit/test_aliyun_oss_storage.py`
2. 合并配置项到新项目：
   - `backend/app/core/config.py`
   - `backend/.env.example`
3. 安装依赖：
   - `cd backend && uv sync`
4. 默认保持 `OSS_ENABLED=false`
5. 仅在需要对象存储的用户故事中开启并注入使用

---

## 输出模板

执行后输出：

1. 修改文件列表
2. 是否需要 Alembic migration（通常否）
3. 实际验证命令
4. 风险点（凭证配置错误、endpoint/cname 配置错误、大文件内存开销）
