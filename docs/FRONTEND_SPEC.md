# 前端架构与工程规范法典
Frontend Engineering Specification for AI-assisted Development  
适用范围：React 19 + Next.js 15+ App Router + TypeScript + Tailwind CSS 4

---

## 0. 总目标

本规范用于约束 AI 编码智能体和人类开发者，目标是：

1. 保持代码可维护、可测试、可扩展。
2. 优先利用 Next.js App Router、React Server Components、Server Functions 的架构优势。
3. 明确 Server / Client / API / State 的职责边界。
4. 避免 AI 生成重复、过度封装、错误鉴权、错误状态管理和样式混乱的代码。

---

## 1. 技术栈基线

### 1.1 必选技术

- 框架：React 19.x + Next.js 15+，使用 App Router。
- 语言：TypeScript，开启 strict 模式。
- 样式：Tailwind CSS 4，采用 CSS-first 配置。
- UI 基础组件：shadcn/ui + Radix UI + Lucide React。
- 表单：React Hook Form + Zod。
- 服务端状态 / 客户端异步状态：TanStack Query。
- 客户端共享状态：Zustand，仅用于 UI 状态和非敏感偏好。
- 校验：Zod，用于表单输入、Server Actions、Route Handlers、外部 API 响应边界。
- 测试：
  - Vitest：工具函数、hooks、纯逻辑。
  - React Testing Library：客户端组件行为。
  - Playwright：核心业务 E2E。
  - MSW：API mock。
- 质量工具：
  - ESLint Flat Config
  - Prettier
  - TypeScript `tsc --noEmit`
  - `next build`

### 1.2 默认不用或慎用

- 不默认使用 Redux。
- 不默认使用 CSS Modules。
- 不默认使用 Axios 作为服务端数据请求工具。
- 不默认使用全局状态保存服务端数据。
- 不在 localStorage / Zustand persist 中保存 JWT、refresh token、session token 等敏感凭证。
- 不在 Server Components 中读取或写入 Zustand store。

---

## 2. 架构原则

### 2.1 Server Components First

默认所有 `app/` 下的 page、layout、普通组件均为 Server Component。

只有满足以下条件之一，才允许添加 `'use client'`：

- 使用 `useState`、`useEffect`、`useRef`、`useReducer` 等客户端 hooks。
- 绑定浏览器事件，如 `onClick`、`onChange`、拖拽、键盘事件。
- 使用浏览器 API，如 `window`、`document`、localStorage、ResizeObserver。
- 使用必须运行在客户端的第三方库。
- 使用 TanStack Query、Zustand、React Hook Form。

禁止为了“方便”在 `page.tsx`、`layout.tsx` 顶部添加 `'use client'`。  
应将交互部分下沉到局部 Client Component。

---

### 2.2 Server / Client 边界

#### Server 侧适合做：

- 数据预取。
- 鉴权和权限判断。
- 访问数据库、内部服务、密钥和私有环境变量。
- 调用外部 API。
- 输入校验。
- 缓存和 revalidate。
- SEO 相关渲染。

#### Client 侧适合做：

- 表单交互。
- 局部 UI 状态。
- 乐观更新。
- 弹窗、抽屉、Toast、筛选器、拖拽、图表交互。
- 需要浏览器能力的功能。

---

### 2.3 响应式设计顺序

- 所有新功能的 UI 设计 MUST 默认先完成 PC 端（desktop / web）布局，再补齐移动端（mobile web）布局。
- 先输出 PC 端主信息层级、交互流程和视觉稿，再基于同一功能收敛移动端断点方案。
- 移动端设计 MUST 作为桌面端方案的响应式延展，而不是独立重写。
- 若存在明显的移动端优先场景，必须在任务说明或方案中显式标注原因。

### 2.4 类型安全

- 禁止使用裸 `any`。
- 外部输入必须先经过 Zod 校验，包括：
  - 表单输入。
  - URL search params。
  - route params。
  - Server Action 入参。
  - Route Handler body。
  - 第三方 API 响应。
- 允许使用 `unknown` 接收不可信数据，然后通过 Zod parse。
- API response 类型不得手写猜测，应由 schema、OpenAPI 类型或明确接口生成。

推荐响应类型：

```ts
type ActionResult<T> =
  | { ok: true; data: T }
  | {
      ok: false
      message: string
      fieldErrors?: Record<string, string[]>
    }
````

---

## 3. 推荐目录结构

```text
frontend/
  ├── app/
  │   ├── (auth)/
  │   ├── (dashboard)/
  │   ├── api/
  │   ├── layout.tsx
  │   ├── page.tsx
  │   ├── loading.tsx
  │   ├── error.tsx
  │   └── not-found.tsx
  │
  ├── components/
  │   ├── ui/                  # shadcn/ui 生成组件
  │   ├── shared/              # Header, Sidebar, AppShell 等跨业务组件
  │   └── feedback/            # EmptyState, ErrorState, LoadingState 等通用反馈组件
  │
  ├── features/
  │   └── user/
  │       ├── components/      # 业务组件
  │       ├── actions.ts       # Server Actions / Server Functions
  │       ├── queries.ts       # TanStack Query hooks / query keys
  │       ├── schemas.ts       # Zod schemas
  │       ├── types.ts
  │       └── utils.ts
  │
  ├── lib/
  │   ├── auth/
  │   ├── http/
  │   │   ├── server-fetch.ts  # 服务端请求封装
  │   │   └── browser-client.ts # 浏览器请求封装，必要时才用 Axios
  │   ├── env.ts
  │   ├── cn.ts
  │   └── utils.ts
  │
  ├── stores/
  │   └── ui-store.ts
  │
  ├── styles/
  │   └── globals.css          # Tailwind v4 @import 与 @theme
  │
  ├── test/
  │   ├── mocks/
  │   └── setup.ts
  │
  ├── public/
  ├── components.json
  ├── next.config.ts
  ├── eslint.config.mjs
  ├── tsconfig.json
  └── package.json
```

### 目录约束

* `app/` 只负责路由、布局、加载态、错误边界和页面组合。
* 业务逻辑放入 `features/xxx/`。
* `components/ui/` 只放 shadcn/ui 基础组件。
* 跨业务组件放 `components/shared/`。
* 不创建巨大 `services/` 文件夹承载所有 API，应按 feature 就近组织。
* `lib/` 只放跨业务、稳定、基础设施级代码。
* `stores/` 只放客户端 UI 状态，不放服务端业务数据。

---

## 4. shadcn/ui 使用规范

### 4.1 基础原则

* `components/ui/` 中的组件视为基础设施组件。
* 允许为了项目主题、可访问性、variant 扩展进行维护性修改。
* 禁止为了单个业务需求直接改基础组件逻辑。
* 业务差异应通过以下方式实现：

  1. `className`
  2. `variant`
  3. 组合封装
  4. 在 `features/xxx/components/` 中创建业务组件

### 4.2 组件命名

* 基础组件：`Button`、`Dialog`、`Form`。
* 业务组件：`UserProfileCard`、`InvoiceTable`、`ProjectSwitcher`。
* 页面局部组件：可以放在对应 route 或 feature 中，例如 `_components/`，但不应跨 feature 复用。

### 4.3 Toast

默认使用 `sonner`。
不新增旧版 shadcn `toast` 方案。

---

## 5. Tailwind CSS 4 样式规范

### 5.1 样式来源

* 默认使用 Tailwind utility class。
* 使用 `cn()` 合并动态 class。
* 允许保留 `styles/globals.css`，用于：

  * `@import "tailwindcss"`
  * `@theme`
  * 全局 CSS variables
  * body 基础样式
  * 第三方库必要样式
* 不新增 CSS Modules，除非经过明确说明。

### 5.2 禁止项

* 禁止大段 inline style。
* 禁止随意新增全局 class。
* 禁止把复杂样式散落在业务逻辑中。
* 禁止硬编码大量颜色值；应使用 theme token。

### 5.3 允许的例外

以下场景允许 `style={{ ... }}`：

* 动态计算尺寸、坐标、进度、图表位置。
* 第三方库要求。
* CSS 变量注入，例如：

```tsx
<div style={{ '--progress': `${value}%` } as React.CSSProperties} />
```

---

## 6. 数据获取与通信规范

### 6.1 读取数据：优先级

#### 优先级 1：Server Component 直接获取

适用于页面首屏、SEO、无需频繁客户端刷新、无需复杂交互的数据。

```tsx
export default async function Page() {
  const user = await getCurrentUser()
  return <UserProfile user={user} />
}
```

#### 优先级 2：TanStack Query

适用于：

* 客户端筛选、分页、搜索。
* 无限滚动。
* 轮询。
* 乐观更新。
* 用户交互后刷新。
* 多组件共享同一份客户端异步状态。

TanStack Query 不用于替代所有 Server Component 数据获取。

#### 优先级 3：Route Handler

适用于：

* 外部系统调用本项目接口。
* Webhook。
* 文件上传 / 下载。
* 浏览器端必须请求的 BFF 接口。
* 需要显式 HTTP 语义的 API。
* 与非 React 客户端共享接口。

---

### 6.2 修改数据：Server Actions 优先，但不是唯一方案

优先使用 Server Actions / Server Functions 处理与 UI 强绑定的 mutation：

* 创建、编辑、删除。
* 表单提交。
* 简单业务操作。
* mutation 后需要 `revalidatePath` / `revalidateTag` / redirect。

但以下场景应使用 Route Handler：

* Webhook。
* 第三方回调。
* 公开 REST API。
* 文件流式处理。
* 大 body 请求。
* 非浏览器客户端调用。
* 需要特殊 HTTP header / status code 控制。

---

### 6.3 Server Actions 安全规则

每个 Server Action 必须包含：

1. 输入校验。
2. 身份认证。
3. 权限校验。
4. 资源归属校验。
5. 错误归一化。
6. 必要时 revalidate。
7. 不返回敏感字段。

示例：

```ts
'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'

const UpdateNameSchema = z.object({
  name: z.string().min(1).max(50),
})

export async function updateNameAction(
  input: unknown,
): Promise<ActionResult<{ name: string }>> {
  const session = await requireSession()

  const parsed = UpdateNameSchema.safeParse(input)
  if (!parsed.success) {
    return {
      ok: false,
      message: 'Invalid input',
      fieldErrors: parsed.error.flatten().fieldErrors,
    }
  }

  const user = await updateUserName({
    userId: session.user.id,
    name: parsed.data.name,
  })

  revalidatePath('/settings')

  return {
    ok: true,
    data: { name: user.name },
  }
}
```

---

### 6.4 Axios 使用边界

默认服务端请求使用 `fetch` 或内部 SDK。
Axios 仅在以下场景使用：

* 浏览器端调用 BFF。
* 需要统一取消、拦截、上传进度等 Axios 特性。
* 兼容历史接口。

禁止在浏览器 Axios 拦截器中从 localStorage / Zustand 读取 Token 注入 Authorization header。
如果项目使用 Cookie Session，浏览器请求应依赖同源 Cookie 或明确的后端会话机制。

---

## 7. 鉴权与权限

### 7.1 Session 存储

* 认证凭证优先使用 HttpOnly、Secure、SameSite Cookie。
* 不把 access token、refresh token、session token 存入 localStorage、sessionStorage、Zustand persist。
* Zustand persist 只允许保存：

  * 主题偏好。
  * 侧边栏展开状态。
  * 表格列显示配置。
  * 非敏感草稿。

### 7.2 Middleware 职责

`middleware.ts` 只做粗粒度路由保护，例如：

* 未登录用户访问 dashboard 时重定向到登录页。
* 已登录用户访问登录页时重定向到首页。
* 国际化路由处理。
* A/B 分流。

middleware 不替代 Server Action、Route Handler、数据库层的权限校验。

### 7.3 权限校验

每个敏感操作必须在服务端重新验证：

* 当前用户是谁。
* 是否具备角色权限。
* 是否拥有目标资源。
* 是否允许执行该动作。

---

## 8. 状态管理策略

### 8.1 状态分类

| 状态类型      | 推荐方案                              |
| --------- | --------------------------------- |
| 服务端数据     | Server Component / TanStack Query |
| 表单状态      | React Hook Form                   |
| URL 状态    | search params                     |
| 局部 UI 状态  | useState / useReducer             |
| 跨组件 UI 状态 | Zustand                           |
| 认证状态      | 服务端 session / cookie              |
| 持久化偏好     | Zustand persist                   |
| 复杂异步缓存    | TanStack Query                    |

### 8.2 Zustand 使用规则

* Zustand store 必须只在 Client Component 中使用。
* 不在 Server Component 中读写 store。
* store 按领域拆分，避免单一巨型 store。
* selector 必须精确，避免订阅整个 store。
* persist 不存敏感信息。

推荐：

```ts
const isOpen = useUiStore((s) => s.sidebarOpen)
const toggle = useUiStore((s) => s.toggleSidebar)
```

不推荐：

```ts
const store = useUiStore()
```

---

## 9. 表单规范

### 9.1 默认组合

* React Hook Form 管理表单状态。
* Zod 管理校验。
* shadcn/ui Form 组件负责 UI 结构。
* mutation 通过 Server Action 或 TanStack Query mutation 完成。

### 9.2 表单错误

必须区分：

* 字段错误。
* 表单级错误。
* 网络错误。
* 权限错误。
* 未登录错误。
* 服务端未知错误。

### 9.3 提交状态

每个表单必须有：

* pending 状态。
* 禁用重复提交。
* 成功反馈。
* 失败反馈。
* 可访问的错误提示。

---

## 10. 异步 UI 三态规范

每个异步 UI 必须显式处理：

1. Loading
2. Error
3. Empty
4. Success

页面级 loading 使用 `loading.tsx` 或 Suspense。
页面级错误使用 `error.tsx`。
局部模块错误使用 `ErrorState`。
空数据使用 `EmptyState`。

禁止只写 happy path。

---

## 11. 路由规范

### 11.1 App Router

* 使用 route groups 管理布局分区。
* 使用 nested layout 管理业务域布局。
* 使用 `loading.tsx` 处理页面加载。
* 使用 `error.tsx` 处理页面错误。
* 使用 `not-found.tsx` 处理 404。
* 使用 `generateMetadata` 管理 SEO metadata。

### 11.2 高级路由

以下场景可以使用 Parallel Routes / Intercepting Routes：

* 弹窗路由。
* 多面板工作台。
* 保持背景页面上下文的详情页。
* 复杂 dashboard。

不要为了普通页面过度使用高级路由。

---

## 12. 错误处理规范

### 12.1 错误分类

* ValidationError：输入错误。
* UnauthorizedError：未登录。
* ForbiddenError：无权限。
* NotFoundError：资源不存在。
* ConflictError：业务冲突。
* RateLimitError：频率限制。
* InternalError：未知错误。

### 12.2 用户可见错误

用户界面不得直接展示原始异常堆栈。
应展示可理解、可行动的错误文案。

### 12.3 日志

服务端错误应记录：

* request id
* user id，如有
* action name / route
* error message
* stack
* 关键业务上下文

不得记录：

* 密码
* token
* cookie
* 完整身份证件
* 银行卡
* 其他敏感隐私数据

---

## 13. 测试规范

### 13.1 测试分层

| 层级       | 工具                    | 必测内容             |
| -------- | --------------------- | ---------------- |
| 单元测试     | Vitest                | utils、schema、纯函数 |
| 组件测试     | React Testing Library | 表单、交互组件、状态变化     |
| API mock | MSW                   | 前后端契约、错误场景       |
| E2E      | Playwright            | 登录、核心创建/编辑/删除流程  |
| 可访问性     | Playwright + axe      | 核心页面基础 a11y      |

### 13.2 必测路径

* 登录 / 登出。
* 权限拦截。
* 核心表单提交。
* 核心数据列表。
* 关键异常分支。
* 空状态。
* 主要移动端布局。
* 响应式设计顺序需先 PC 端再移动端。

### 13.3 Storybook

复杂 UI 组件、设计系统组件、可复用业务组件应提供 stories。

每个 story 至少覆盖：

* default
* loading
* error
* empty
* long content
* mobile width

---

## 14. 性能规范

### 14.1 Client Bundle 控制

* 不把大型库引入 Server Component 后再传给 Client Component。
* 图表、富文本、地图等重型组件应动态加载。
* Client Component 越小越好。
* 避免在根布局引入大型客户端 Provider。

### 14.2 图片与字体

* 图片优先使用 `next/image`。
* 字体优先使用 `next/font`。
* 静态资源放入 `public/`。
* 大图必须设置合理尺寸、懒加载和占位策略。

### 14.3 渲染策略

* 稳定公共内容优先缓存。
* 用户私有内容避免错误共享缓存。
* mutation 后明确 revalidate。
* 避免无意识 `no-store` 导致所有页面动态化。

---

## 15. 可访问性规范

所有交互组件必须满足：

* 可键盘操作。
* 有明确 focus 样式。
* 表单控件有 label。
* 图标按钮有 aria-label。
* 弹窗、下拉菜单使用 Radix / shadcn 基础组件。
* 错误提示能被屏幕阅读器感知。
* 不只依赖颜色表达状态。

---

## 16. 代码风格

### 16.1 组件

* 使用函数组件。
* Props 使用 `type` 或 `interface` 明确定义。
* Props 解构。
* 组件文件建议不超过 250 行。
* 超过 250 行应拆分：

  * 子组件
  * hook
  * schema
  * utils
  * constants

### 16.2 命名

* 组件：PascalCase。
* hook：`useXxx`。
* Server Action：`xxxAction`。
* schema：`XxxSchema`。
* query key factory：`xxxKeys`。
* store：`useXxxStore`。

### 16.3 Import

推荐顺序：

1. React / Next
2. 第三方库
3. 项目 alias
4. 相对路径
5. 类型导入
6. 样式

---

## 17. 环境变量

* 服务端环境变量统一通过 `lib/env.ts` 校验。
* 客户端环境变量必须以 `NEXT_PUBLIC_` 开头。
* 不在 Client Component 中读取服务端密钥。
* 启动时应校验必需环境变量，避免运行时才失败。

---

## 18. AI 编码智能体行为约束

AI 生成代码时必须遵守：

1. 不无故把 Server Component 改成 Client Component。
2. 不无故引入新依赖。
3. 不创建重复的组件、hook、schema、store。
4. 修改前先复用现有目录结构和工具函数。
5. 涉及 mutation 时必须包含校验、鉴权、错误处理和 revalidate。
6. 涉及表单时必须包含 pending、error、success 状态。
7. 涉及 API 响应时必须处理 loading、error、empty。
8. 涉及权限时不得只依赖前端隐藏按钮。
9. 涉及敏感数据时不得进入 localStorage、Zustand persist、console log。
10. 输出代码后必须说明需要执行的验证命令。

---

## 19. 交付门禁

提交前必须通过：

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build
```

核心业务改动还必须通过：

```bash
pnpm test:e2e
```

如果修改 UI 基础组件，应额外检查：

```bash
pnpm storybook
pnpm build-storybook
```

---

## 20. Definition of Done

一个前端任务完成必须满足：

* 功能满足需求。
* 类型检查通过。
* Lint 通过。
* 构建通过。
* 关键路径有测试或说明无需测试的理由。
* Loading / Error / Empty / Success 状态完整。
* 移动端布局可用。
* PC 端方案已先行设计并落地。
* 基础可访问性可用。
* 无敏感信息泄漏。
* 无无用 console。
* 无未解释的新依赖。



