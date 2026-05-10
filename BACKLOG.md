# 需求池（Backlog）

> 日常开发禁读此文件。由 PM 角色维护。
> 默认由 `/pm-plan` 维护；`/sprint-plan` 仅从 Ready 条目中挑选进入 Sprint。
> 条目必须包含：`story_id`、`Priority`、`Status`、`User Story`、`Acceptance Criteria`、`In Scope`、`Out of Scope`、`Dependencies/Risks`。

## P0（必须做）

<!-- 推荐条目模板（复制使用）：
- [ ] story_id: US-YYYYMMDD-01
  - Priority: P0
  - Status: Draft | Ready | In Sprint | Done
  - User Story: 作为 <角色>，我希望 <目标>，以便 <价值>
  - Acceptance Criteria:
    - [ ] 条件 1
    - [ ] 条件 2
  - In Scope:
    - <本轮包含项>
  - Out of Scope:
    - <本轮不做项>
  - Dependencies/Risks:
    - 依赖：<无/说明>
    - 风险：<无/说明>
-->

- [ ] story_id: US-20260510-01
  - Priority: P0
  - Status: Ready
  - User Story: 作为新用户，我希望可以通过邮箱和密码完成注册，以便开始使用平台能力
  - Acceptance Criteria:
    - [ ] 提交邮箱+密码后可创建账号，并返回标准成功响应
    - [ ] 对已存在邮箱注册时返回明确错误码与错误信息
    - [ ] 注册成功后可在登录接口使用同一凭证完成登录
  - In Scope:
    - 注册接口（输入校验、冲突校验、成功响应）
    - 注册最小前端表单（PC 端优先，随后补齐移动端响应式）
  - Out of Scope:
    - 第三方社交登录（OAuth）
    - 邮件验证码服务接入
  - Dependencies/Risks:
    - 依赖：用户表 Schema、密码哈希组件
    - 风险：密码强度规则未统一可能导致前后端校验不一致

- [ ] story_id: US-20260510-02
  - Priority: P0
  - Status: Ready
  - User Story: 作为已注册用户，我希望可以通过邮箱和密码登录，以便访问受保护资源
  - Acceptance Criteria:
    - [ ] 输入正确凭证时返回 access token 与 refresh token
    - [ ] 输入错误凭证时返回统一鉴权失败响应，不泄露账号是否存在
    - [ ] 登录成功后前端可访问受保护页面并正确处理会话状态
  - In Scope:
    - 登录接口（鉴权校验、Token 签发、错误响应）
    - 登录前端交互与受保护页面跳转
  - Out of Scope:
    - 多因子认证（MFA）
    - 设备管理与异地登录提醒
  - Dependencies/Risks:
    - 依赖：JWT 配置、认证中间件、受保护路由守卫
    - 风险：Token 过期策略未定可能影响前端刷新逻辑

## P1（应该做）

- [ ] story_id: US-20260510-03
  - Priority: P1
  - Status: Ready
  - User Story: 作为已登录用户，我希望可以修改个人资料，以便保持个人信息最新且准确
  - Acceptance Criteria:
    - [ ] 可更新昵称与个人简介，并返回最新用户信息
    - [ ] 头像上传失败时返回明确错误信息且不影响原数据
    - [ ] 未登录状态访问资料更新接口时返回未授权响应
  - In Scope:
    - 个人资料查询与更新接口
    - 个人资料编辑表单与基础校验
  - Out of Scope:
    - 头像图片裁剪与高级编辑
    - 个人主页公开展示页重构
  - Dependencies/Risks:
    - 依赖：鉴权中间件、对象存储方案（若启用头像文件存储）
    - 风险：头像上传链路未统一可能导致前后端错误处理不一致

## P2（可以做）

- [ ] story_id: US-20260510-04
  - Priority: P2
  - Status: Ready
  - User Story: 作为管理员，我希望可以查看用户列表并按条件筛选，以便进行日常运营管理
  - Acceptance Criteria:
    - [ ] 支持分页查询用户列表，并返回总量与分页信息
    - [ ] 支持按邮箱或昵称关键字筛选
    - [ ] 非管理员访问该接口时返回权限不足错误
  - In Scope:
    - 管理端用户列表 API（分页、筛选）
    - 管理后台用户列表页面基础展示
  - Out of Scope:
    - 用户封禁/解禁操作
    - 批量导出与审计报表
  - Dependencies/Risks:
    - 依赖：管理员角色权限模型、查询索引策略
    - 风险：数据量增大时分页查询性能可能不足

## 已完成（移入 CHANGELOG.md）
