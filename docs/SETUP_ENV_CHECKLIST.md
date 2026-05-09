# /setup 环境变量替换检查清单（Checklist）

> 目的：在 `/setup` 完成项目名注入后，指导用户将模板值替换为真实环境变量，并可由脚本逐项校验。

---

## 1) 根目录（Docker Compose）`.env.example`

- [ ] `POSTGRES_USER`：已确认为项目实际数据库用户名
- [ ] `POSTGRES_PASSWORD`：不为 `changeme`
- [ ] `POSTGRES_DB`：已确认为项目实际数据库名

---

## 2) 后端 `backend/.env.example`

### 基础配置
- [ ] `APP_NAME`：与项目名一致
- [ ] `APP_ENV`：与实际环境匹配（如 `local` / `staging` / `production`）
- [ ] `DEBUG`：生产环境为 `false`
- [ ] `DATABASE_URL`：不包含 `changeme`，连接信息正确
- [ ] `DATABASE_TEST_URL`：不包含 `changeme`，连接信息正确
- [ ] `CORS_ORIGINS`：已按实际前端来源配置

### 安全与密钥
- [ ] `JWT_PRIVATE_KEY`：非空
- [ ] `JWT_PUBLIC_KEY`：非空

### 对象存储（OSS）
- [ ] `OSS_ACCESS_KEY_ID`：非空
- [ ] `OSS_ACCESS_KEY_SECRET`：非空
- [ ] `OSS_BUCKET_NAME`：非空
- [ ] `OSS_ENDPOINT`：非空

### 邮件（SMTP）
- [ ] `SMTP_HOST`：非空
- [ ] `SMTP_PORT`：已确认端口
- [ ] `SMTP_USERNAME`：非空
- [ ] `SMTP_PASSWORD`：非空
- [ ] `SMTP_FROM_EMAIL`：非空

### 可观测性（Observability）
- [ ] `OTEL_EXPORTER_ENDPOINT`：按环境配置（本地可空，非本地建议填写）

---

## 3) 前端 `frontend/.env.example`（如存在）

- [ ] 已创建或确认前端环境变量模板
- [ ] 所有 `NEXT_PUBLIC_*` 变量已填写为真实值
- [ ] 未将敏感密钥暴露为 `NEXT_PUBLIC_*`

---

## 4) 替换后逐项检查命令

```bash
uv run scripts/check_env_replacements.py
```

检查通过标准：
- 输出中无 `FAIL`
- 若有 `WARN`，需人工确认是否符合当前环境策略
