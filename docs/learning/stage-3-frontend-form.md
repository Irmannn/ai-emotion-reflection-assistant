# 阶段 3：前端表单、状态与历史记录

## 阶段目标

- 实现情绪复盘表单。
- 前端生成并保存匿名 `session_id`。
- 实现历史记录列表、详情展示、删除记录。
- 与阶段 2 后端 CRUD 接口联调。

## 目录设计

- `frontend/app/types/`：前端类型定义。
- `frontend/app/lib/`：工具函数和 API 请求封装。
- `frontend/app/components/`：展示组件和局部交互组件。
- `frontend/app/page.tsx`：页面容器组件，负责状态和业务流程编排。

这样拆分是为了避免所有逻辑堆在 `page.tsx`，也方便后续接入 LLM 和流式输出。

## 类型与 API

### `types/reflection.ts`

前端版 API 数据合同，对应后端 `schemas.py` 和 `/docs`。

- `ReflectionFormValues`：表单内部数据。
- `CreateReflectionPayload`：创建请求体。
- `ReflectionListItem`：历史列表项。
- `ReflectionDetail`：详情响应。

### `lib/session.ts`

用 `localStorage` 保存匿名 `session_id`。

- `localStorage`：刷新、关闭浏览器、重启后通常仍存在。
- `sessionStorage`：当前标签页会话结束后清空。
- `crypto.randomUUID()`：浏览器内置 Web Crypto API，用来生成随机 UUID。

### `lib/api.ts`

前端请求后端的统一入口。

重要概念：

- `import type`：只导入 TS 类型，不进入运行时代码。
- `process.env.NEXT_PUBLIC_*`：Next.js 暴露给浏览器的环境变量。
- `??`：空值合并运算符。
- `<T>`：泛型类型参数。
- `Promise<T>`：异步成功时 resolve 出 `T`，失败时 reject 错误。
- `RequestInit`：浏览器 `fetch` 第二个参数的类型。
- `URLSearchParams`：生成和编码 query 参数。
- `method: "DELETE"`：调用 REST 删除接口。

## React 表单

### Client Component

使用 `useState`、`useEffect`、事件、`localStorage` 等浏览器能力时，需要 `"use client"`。

### Hook

Hook 是 React 提供的函数，让函数组件拥有状态、副作用等能力。

- `useState`：管理组件状态。
- `useEffect`：处理渲染后的副作用。

### 受控表单

受控表单是表单值由 React state 控制。

```tsx
value={values.event_text}
onChange={(event) => setValues({ ...values, event_text: event.target.value })}
```

好处：

- 提交时直接拿完整 `values`。
- 可以实时校验。
- 可以控制按钮 disabled。
- 可以提交成功后重置表单。

### `setValues((current) => ...)`

函数式更新。`current` 是 React 传入的当前最新状态，适合新状态依赖旧状态的场景。

### `event.preventDefault()`

阻止浏览器原生 form 提交刷新页面，由 React 自己调用接口。

### `type="button"`

form 内普通按钮应显式写 `type="button"`，否则可能被当成 submit 触发表单提交。

## TSX 语法

- 固定字符串属性用 `"..."`。
- JS/TS 表达式用 `{...}`。
- Vue `{{}}` 类似文本插值；TSX `{}` 是页面结构中的 JS 表达式。
- 模板字符串 `` `${}` `` 是字符串内部插值。
- `.tsx` 是 TypeScript + JSX。

## 时间显示

后端 datetime 通过 JSON 返回会变成字符串。SQLite 读出时可能丢失时区标记。

阶段 3 在前端做兼容：

- 如果字符串有 `Z` 或 `+08:00` 这类时区标记，直接解析。
- 如果没有时区标记，就补 `Z` 按 UTC 解析。
- 用 `toLocaleString("zh-CN", { timeZone: "Asia/Shanghai", hour12: false })` 显示北京时间和 24 小时制。

## `page.tsx`

`page.tsx` 是阶段 3 的容器组件/编排层：

- 初始化 `session_id`。
- 加载历史列表。
- 创建记录。
- 选择详情。
- 删除记录。
- 管理 loading / error / selectedRecord。
- 把状态和回调传给子组件。

### `useEffect(..., [])`

空依赖数组表示首次挂载后执行一次。

### `setState` 不是立即改当前变量

`setSessionId(nextSessionId)` 会调度下一次渲染，当前闭包里的 `sessionId` 仍可能是旧值。所以首次加载列表时用立即可用的局部变量 `nextSessionId`。

## 阶段卡点

- Next.js 在 `/mnt/c` 下曾出现 `.next` chunk/module 错误，重启并清缓存可恢复。
- SQLite 在 `/mnt/c` 下曾出现 readonly database，迁移到 WSL 原生目录更稳定。
- 表单生成失败后清空输入是交互 bug，已修复为成功才清空，失败保留输入。

## 阶段复盘

- 日期：2026-07-03
- 已完成：表单、session、历史列表、详情、删除。
- 验证结果：浏览器联调通过，Network 中 POST/GET/DELETE 请求符合预期。
