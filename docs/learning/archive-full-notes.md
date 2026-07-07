# 学习疑问与笔记

这个文件用于记录从前端开发转型到 LLM / Agent 应用工程师过程中的结构化问题、阶段结论和实践复盘。

## 使用方式

- 遇到不懂的问题，先记录到「待解决问题」。
- 通过项目实践得到答案后，整理到对应分类。
- 每完成一个阶段，补充一次「阶段复盘」。
- 保留问题演进过程，不只记录最终答案。

## 目录

- [基础全栈工程能力](#基础全栈工程能力)
- [LLM 应用基础](#llm-应用基础)
- [RAG](#rag)
- [Agent 与工作流](#agent-与工作流)
- [生产化与运维](#生产化与运维)
- [项目实践记录](#项目实践记录)
- [阶段复盘](#阶段复盘)
- [待解决问题](#待解决问题)

## 基础全栈工程能力

### 前端

| 问题 | 当前理解 | 实践来源 | 状态 |
| --- | --- | --- | --- |
| 如何用前端处理流式输出？ | 待补充 | 阶段 5 | 未开始 |
| 什么是同源和跨域？ | 浏览器判断同源看三项：协议、完整主机名、端口。三者完全一致才是同源，任意一个不同就是跨域。例如 `http://localhost:3000` 请求 `http://localhost:8000`，协议和主机名相同，但端口不同，所以是跨域。 | 阶段 1 | 已记录 |
| URL 里没写端口时怎么判断端口？ | 没写端口时浏览器使用协议默认端口：`http` 默认 80，`https` 默认 443。所以 `https://example.com` 等价于 `https://example.com:443`。 | 阶段 1 | 已记录 |
| 域名/主机名怎么理解？ | URL 结构是 `协议://主机名:端口/路径?查询参数`。例如 `https://api.example.com:443/users?id=1` 里，协议是 `https`，完整主机名是 `api.example.com`，端口是 `443`，路径是 `/users`。浏览器判断同源时看完整主机名，所以 `api.example.com` 和 `www.example.com` 不同源。 | 阶段 1 | 已记录 |
| CORS 是什么？ | CORS 是浏览器的跨域安全机制。当前项目中前端是 `http://localhost:3000`，后端是 `http://localhost:8000`，端口不同所以跨域。后端需要明确允许 `http://localhost:3000`，前端浏览器才允许页面读取后端响应。 | 阶段 1 | 已记录 |
| `.nvmrc` 是做什么的？ | `.nvmrc` 用来声明项目期望的 Node.js 版本。本项目写的是 `20`。在 macOS/Linux 的 nvm 里，`nvm use` 通常会向上查找 `.nvmrc`；但 Windows 的 nvm-windows / Git Bash 场景可能要求显式写版本，所以 README 使用 `nvm use 20`。 | 阶段 1 | 已记录 |
| `npm install` 和 `npm ci` 有什么区别？ | `npm install` 用于首次创建项目、新增依赖、升级依赖，可能会更新 `package-lock.json`；`npm ci` 用于已有 `package-lock.json` 的干净安装，会严格按锁文件安装，通常不用于新增依赖。刚 clone 项目、验证项目可复现、CI 自动构建时，优先用 `npm ci`。 | 阶段 1 | 已记录 |
| 为什么当前用 npm 而不是 yarn？ | Node 自带 npm，初学阶段变量更少；项目已生成 `package-lock.json`，继续用 npm 可以避免同时存在 `package-lock.json` 和 `yarn.lock`。如果未来切换 yarn/pnpm，需要删除旧锁文件并统一 README 命令。 | 阶段 1 | 已记录 |
| 为什么说 `npm ci` 可以验证锁文件可复现？ | `package.json` 里经常写版本范围，例如 `^15.0.0`；`package-lock.json` 记录实际安装的精确版本。`npm ci` 不重新决定依赖版本，而是严格按锁文件安装。如果它能在干净环境安装成功，说明别人 clone 仓库后也能重建一致的依赖环境。 | 阶段 1 | 已记录 |
| `package-lock.json` 里的 `version`、`resolved`、`integrity` 是什么？ | `version` 是某个依赖实际锁定的版本；`resolved` 是该依赖包的下载地址；`integrity` 是完整性校验值，用来确认下载到的包内容没有被篡改。阶段 1 不需要逐行看锁文件，但要知道它记录完整依赖树的精确安装信息。 | 阶段 1 | 已记录 |
| `npm ci --prefer-offline` 是什么意思？ | `--prefer-offline` 表示优先使用本地 npm 缓存，缓存缺失时仍然允许联网下载。它不是完全离线，和 `--offline` 不同。适合网络不稳定、但之前已经下载过一部分依赖的场景。 | 阶段 1 | 已记录 |
| CI/CD 自动构建是什么意思？ | CI 是 Continuous Integration，持续集成，指代码提交后自动安装依赖、构建和测试，检查代码是否可用；CD 是 Continuous Delivery/Deployment，持续交付/部署，指检查通过后自动发布到环境。当前项目暂不做 CI/CD，但锁文件、Node 版本和构建命令是在为后续自动构建做准备。 | 阶段 1 | 已记录 |
| `.next` 是什么？ | `.next` 是 Next.js 自动生成的构建/运行缓存目录。执行 `npm run dev` 或 `npm run build` 后会生成，里面包含编译后的页面代码、构建缓存、路由信息和静态产物。它是本地生成物，不需要手写或查看，也不提交 GitHub，已通过 `.gitignore` 忽略。 | 阶段 1 | 已记录 |
| Next.js 是什么？ | Next.js 是基于 React 的应用框架。React 主要负责 UI 组件和状态到界面的渲染；Next.js 在 React 之上提供路由、构建、开发服务器、服务端渲染、静态生成、元信息和部署约定等工程能力。可以简单理解为：React 是 UI 库，Next.js 是基于 React 的应用框架。 | 阶段 1 | 已记录 |
| 写 React 一定要用 Next.js 吗？ | 不一定。React + Vite 更适合后台管理系统、内部工具、普通 SPA、前后端明确分离且 SEO 不重要的项目；React + Next.js 更适合官网、内容站、需要 SEO/SSR/SSG、需要文件路由或更完整工程约定的产品型应用。 | 阶段 1 | 已记录 |
| 当前项目为什么选 Next.js？ | 这个项目目标是做一个 AI 产品 MVP，而不是单纯后台页面。Next.js 在 AI Web App、SaaS Demo、简历项目中识别度高，路由和工程约定完整，后续也方便扩展页面、Markdown 展示、部署和可能的全栈能力。 | 阶段 1 | 已记录 |
| `dependencies` 和 `devDependencies` 有什么区别？ | `dependencies` 是应用运行时需要的包，例如 `next`、`react`、`react-dom`；`devDependencies` 主要用于开发、构建和类型检查，例如 `typescript`、`tailwindcss`、`postcss`、`@types/react`。简单判断：用户访问网站时还需要它，通常放 `dependencies`；只在开发或构建工具链中使用，通常放 `devDependencies`。 | 阶段 1 | 已记录 |
| `tsconfig.json` 当前需要理解到什么程度？ | `tsconfig.json` 是 TypeScript 配置文件，告诉 TS 如何检查项目代码。阶段 1 不需要背所有字段，重点记住 5 个点：`strict: true` 开启严格类型检查；`noEmit: true` 表示 TS 只检查类型、不输出 JS；`jsx: "preserve"` 表示 JSX 交给 Next.js/React 编译链处理；`include`/`exclude` 控制哪些文件参与检查；其他大多可先视为 Next.js 标准模板配置。 | 阶段 1 | 已记录 |
| `tailwind.config.ts` 是做什么的？ | 它是 Tailwind CSS 的配置文件。阶段 1 重点理解两件事：`content` 告诉 Tailwind 去哪些文件里扫描 class；`theme.extend` 用于扩展项目自己的主题 token，例如自定义颜色。 | 阶段 1 | 已记录 |
| Tailwind 的 `content` 配置为什么重要？ | Tailwind 会扫描 `content` 指定的文件，找出代码里实际使用过的 class，并生成对应 CSS。如果某个目录没有写进 `content`，那个目录里的 Tailwind class 可能不会生效。本项目扫描 `app/` 和未来可能出现的 `components/`。 | 阶段 1 | 已记录 |
| `text-ink`、`bg-sage` 这种写法是什么意思？ | Tailwind class 通常是“用途前缀 + 主题值”。`text-ink` 表示文字颜色使用 `ink`，等价于 `color: #172033`；`bg-sage` 表示背景色使用 `sage`，等价于 `background-color: #7da391`。`ink`、`sage` 来自 `tailwind.config.ts` 的自定义 colors。 | 阶段 1 | 已记录 |
| `text-lg` 里的 `lg` 也需要自己定义吗？ | 不需要。`lg` 是 Tailwind 内置字号 token，所以 `text-lg` 可以直接用。`ink`、`sage`、`clay` 是项目自定义 token，需要在 `tailwind.config.ts` 里定义。可以简单记：内置 token 可直接用，自定义 token 要在配置里声明。 | 阶段 1 | 已记录 |
| `postcss.config.js` 是做什么的？ | PostCSS 可以理解为 CSS 处理流水线。`postcss.config.js` 告诉构建工具使用哪些 PostCSS 插件。本项目配置了 `tailwindcss` 和 `autoprefixer`：前者把 Tailwind 指令和 class 转成真实 CSS，后者自动补部分浏览器兼容前缀。阶段 1 只需要知道它让 Tailwind 和 CSS 兼容处理生效。 | 阶段 1 | 已记录 |
| Tailwind 是什么？ | Tailwind 是 utility-first / 原子化 CSS 框架。它通过大量小工具类组合 UI，例如 `rounded-3xl` 设置圆角、`bg-white` 设置背景色、`p-8` 设置内边距。优点是写页面快、不用频繁命名 CSS class；缺点是 `className` 可能较长，需要熟悉规则。 | 阶段 1 | 已记录 |
| `@tailwind base/components/utilities` 是什么？ | 这三行是 Tailwind 的全局样式入口。`@tailwind base` 注入基础样式和浏览器样式重置；`@tailwind components` 注入组件层样式；`@tailwind utilities` 注入最常用的工具类样式，例如 `flex`、`grid`、`text-lg`、`bg-sage`。 | 阶段 1 | 已记录 |
| `next.config.ts` 是做什么的？ | 它是 Next.js 的项目配置文件。当前配置对象为空，表示使用 Next.js 默认配置。后续需要图片域名、rewrites/proxy、构建输出或部署选项时再修改。 | 阶段 1 | 已记录 |
| `next-env.d.ts` 是什么？ | 它是 Next.js 自动维护的 TypeScript 类型声明入口，让 TypeScript 认识 Next.js 提供的全局类型、图片类型和生成的路由类型。`.d.ts` 表示 declaration file，只描述类型。这个文件不要手动编辑。 | 阶段 1 | 已记录 |
| `layout.tsx` 里的 `RootLayout` 语法怎么理解？ | `export default function RootLayout(...)` 定义并默认导出布局组件，Next.js 会识别 `app/layout.tsx` 的默认导出作为全局布局。参数里的 `{ children }` 是对象解构，等价于从 `props.children` 取出页面内容。`: Readonly<{ children: React.ReactNode }>` 是 TypeScript 类型声明，表示参数对象只读，且 `children` 是 React 可渲染内容。`return (...)` 返回 TSX，`<body>{children}</body>` 用花括号把页面内容插入到 body 中。 | 阶段 1 | 已记录 |
| 为什么 `layout.tsx` 没有 import `page.tsx`？ | 这是 Next.js App Router 的文件约定。`app/page.tsx` 自动对应首页 `/`，`app/layout.tsx` 自动作为该目录下页面的布局。Next.js 会自动把页面组件作为 `children` 传给布局组件，类似自动组合 `<RootLayout><Home /></RootLayout>`，不需要手动 import。 | 阶段 1 | 已记录 |
| `.tsx` 是什么？ | `.tsx` 表示 TypeScript + JSX。`.ts` 适合没有 JSX 的普通 TypeScript 逻辑文件；`.tsx` 适合写 React 组件，因为组件里会返回类似 HTML 的 JSX/TSX 结构，例如 `<main><h1>...</h1></main>`。 | 阶段 1 | 已记录 |
| React 组件为什么是函数返回类似 HTML 的内容？ | React 组件通常是返回 UI 描述的函数。函数返回的不是普通 HTML 字符串，而是 JSX/TSX，React/Next.js 会把它编译并渲染成浏览器 DOM。当前阶段先理解：React 页面由组件函数组成，组件函数 `return` TSX，TSX 描述页面 UI。 | 阶段 1 | 已记录 |
| 阶段 3 前端为什么拆成 `types`、`lib`、`components` 和 `page.tsx`？ | 这样拆是为了让职责清晰：`types/` 只定义前端数据结构；`lib/` 放工具和后端 API 请求；`components/` 只负责 UI 展示和局部交互；`page.tsx` 负责页面编排、状态管理和业务流程协调。好处是避免所有代码堆在 `page.tsx`，也方便后续阶段替换创建逻辑、接入 LLM 和继续扩展页面。 | 阶段 3 | 已记录 |
| `localStorage` 和 `sessionStorage` 有什么区别？ | 两者都是浏览器本地存储。`localStorage` 通常会持久保存在本地磁盘上，刷新页面、关闭浏览器、关机重启后一般仍然存在，直到用户清理站点数据或代码主动删除；`sessionStorage` 通常只在当前标签页会话内有效，关闭标签页后就会清空。当前项目用 `localStorage` 保存匿名 `session_id`，是为了没有登录系统时也能在下次打开页面后继续看到历史记录。 | 阶段 3 | 已记录 |
| `crypto.randomUUID()` 是什么？ | `crypto` 是浏览器内置的全局对象，属于 Web Crypto API，不是 npm 包，所以不需要 import；`crypto.randomUUID()` 用来生成随机 UUID 字符串，例如 `9f3b7f61-6a44-4f87-9df0-7e4c5f0e2a91`。当前项目用它生成匿名 `session_id`，比 `Math.random()` 更适合做唯一标识。 | 阶段 3 | 已记录 |
| `import type` 是什么意思？ | `import type` 只导入 TypeScript 类型，不导入运行时代码。类型只在编译检查时存在，浏览器真正运行的 JavaScript 里没有这些类型。当前 `types/reflection.ts` 只定义类型，没有真实函数逻辑，所以用 `import type` 更准确。 | 阶段 3 | 已记录 |
| `import` 什么时候要用 `{}`？ | 如果目标文件使用命名导出，例如 `export function xxx` 或 `export type Xxx`，导入时使用 `{ xxx }`；如果目标文件使用 `export default` 默认导出，导入时不用 `{}`，可以自己命名。 | 阶段 3 | 已记录 |
| `process.env.NEXT_PUBLIC_API_BASE_URL` 在哪里配置？ | 它是 Next.js 环境变量，通常可以写在 `frontend/.env.local`。当前项目还没配置，所以代码会使用兜底地址 `http://localhost:8000`。Next.js 中只有 `NEXT_PUBLIC_` 开头的环境变量会暴露给浏览器端代码。 | 阶段 3 | 已记录 |
| `??` 是三元表达式吗？ | 不是。`??` 是空值合并运算符，表示左侧是 `null` 或 `undefined` 时使用右侧兜底值；三元表达式是 `condition ? valueA : valueB`。 | 阶段 3 | 已记录 |
| TypeScript 里的 `<T>` 是什么？ | `<T>` 可以理解成类型变量/泛型参数。函数定义时不把返回数据类型写死，而是在调用时指定，例如 `request<ReflectionDetail>(...)` 表示这次请求期望返回 `ReflectionDetail`。 | 阶段 3 | 已记录 |
| 为什么 `request<T>` 会影响返回值类型？ | `request<T>` 里的 `<T>` 是声明这个通用函数有一个类型参数；后面的 `Promise<T>` 是使用这个类型参数作为返回值类型。如果去掉 `request<T>` 里的 `<T>`，`Promise<T>` 中的 `T` 就没有来源。调用 `request<ReflectionDetail>(...)` 时，就是告诉这个通用函数：本次请求的 `T` 是 `ReflectionDetail`。 | 阶段 3 | 已记录 |
| `Promise<T>` 是什么？ | `Promise<T>` 表示一个异步结果。成功时 Promise 会 resolve 出 `T` 类型的数据；失败时 Promise 会 reject 一个错误，例如请求函数里 `throw new Error(...)` 会让 async 函数返回失败状态的 Promise。`T` 只描述成功时的数据类型，不代表请求一定成功。 | 阶段 3 | 已记录 |
| 参数名后面的 `?` 是什么意思？ | 在 TypeScript 里，`init?: RequestInit` 表示 `init` 是可选参数，可以传也可以不传。 | 阶段 3 | 已记录 |
| `RequestInit` 是什么？ | `RequestInit` 是浏览器内置的 TypeScript 类型，用来描述 `fetch` 第二个参数的配置结构，例如 `method`、`headers`、`body`、`credentials`、`signal` 等。 | 阶段 3 | 已记录 |
| 模板字符串里的 `${...}` 是什么？ | 这是模板字符串插值语法，必须配合反引号使用。`${API_BASE_URL}${path}` 等价于 `API_BASE_URL + path`，用于拼接完整请求地址。 | 阶段 3 | 已记录 |
| 为什么请求 JSON 要写 `Content-Type: application/json`？ | 如果请求体通过 `JSON.stringify(payload)` 发送 JSON 字符串，就应该设置 `Content-Type: application/json`，告诉后端按 JSON 解析请求体。GET 请求没有 body 时不一定需要，但当前为了封装简单统一加上。上传文件时通常不能手动写这个值，而应让浏览器设置 multipart 边界。 | 阶段 3 | 已记录 |
| `init?.headers` 里的 `?.` 是什么？ | `?.` 是可选链。因为 `init` 可能没传或可能是空值，直接写 `init.headers` 会在 `init` 为 `undefined` 或 `null` 时报错；`init?.headers` 表示如果 `init` 是 `null` 或 `undefined` 就返回 `undefined`，否则读取 `init.headers`。 | 阶段 3 | 已记录 |
| `response.json()` 是做什么的？ | 它会读取后端返回的 JSON 文本，并解析成 JavaScript 对象。例如后端返回 `{"status":"ok"}`，前端调用 `response.json()` 后得到 `{ status: "ok" }`。这个过程也是异步的，所以返回 Promise。 | 阶段 3 | 已记录 |
| `as Promise<T>` 是什么意思？ | `as` 是 TypeScript 类型断言。浏览器原生 `response.json()` 的类型通常比较宽泛，TypeScript 不知道后端具体返回什么结构；`as Promise<T>` 表示告诉 TypeScript：这个 JSON 解析结果可以按当前请求期望的 `Promise<T>` 看待。 | 阶段 3 | 已记录 |
| `new URLSearchParams(...)` 是什么？ | `URLSearchParams` 是浏览器内置对象，用来生成和处理 URL query 参数。`new URLSearchParams({ session_id: sessionId })` 会创建一个 query 参数对象，`params.toString()` 会把它转成 `session_id=xxx` 这种字符串，并自动处理中文、空格、特殊符号的 URL 编码。 | 阶段 3 | 已记录 |
| `Promise<{ deleted: boolean }>` 里可以直接写对象类型吗？ | 可以。TypeScript 允许直接写内联对象类型。`Promise<{ deleted: boolean }>` 表示成功后会得到一个对象，对象里有 `deleted` 布尔字段。对象结构简单时可以内联写，复杂或复用时再单独定义 `type DeleteResponse = { deleted: boolean }`。 | 阶段 3 | 已记录 |
| `method: "DELETE"` 是什么？ | `fetch` 默认请求方法是 GET。如果要调用删除接口，需要显式写 `method: "DELETE"`。在 REST API 中常见方法包括 GET 获取数据、POST 创建/提交、PUT 整体更新、PATCH 局部更新、DELETE 删除数据。 | 阶段 3 | 已记录 |
| REST API 是什么意思？ | REST API 是一种常见后端接口设计风格。简单理解：把后端数据当成资源，用 URL 表示资源，用 HTTP 方法表示动作。例如 `GET /api/reflections` 表示获取复盘列表，`POST /api/reflections` 表示创建复盘，`GET /api/reflections/{id}` 表示获取详情，`DELETE /api/reflections/{id}` 表示删除记录。核心思想是 URL 尽量表达“操作的东西是什么”，HTTP method 表达“要做什么”。 | 阶段 3 | 已记录 |
| Next.js 的 Server Component 和 Client Component 有什么区别？ | App Router 默认组件是 Server Component，主要在服务端执行，适合静态展示、服务端数据读取和不需要浏览器交互的页面结构。需要 `useState/useEffect`、点击/输入事件、`localStorage/window/document` 等浏览器能力时，要在文件顶部写 `"use client"`，让它成为 Client Component。不是所有前端页面都要写 `"use client"`。 | 阶段 3 | 已记录 |
| React Hook 是什么？ | Hook 是 React 提供的一类函数，让函数组件拥有状态、副作用等能力，通常以 `use` 开头。例如 `useState` 管理组件状态，`useEffect` 处理页面加载后的副作用。普通函数可以计算或请求接口，但普通变量变化不会通知 React 重新渲染；用 state 并调用 setState，React 才知道数据变了并更新 UI。 | 阶段 3 | 已记录 |
| `FormEvent<HTMLFormElement>` 是什么？ | 它是 React 表单提交事件的 TypeScript 类型，表示这个 event 来自 HTML 的 `<form>` 元素。事件类型要看绑定在哪个元素上：`form onSubmit` 常用 `FormEvent<HTMLFormElement>`，输入框变化可能是 `ChangeEvent<HTMLInputElement>`、文本域是 `HTMLTextAreaElement`、下拉框是 `HTMLSelectElement`。`FormEvent` 本身不是过时，只是更推荐用 `import type` 导入类型。 | 阶段 3 | 已记录 |
| 为什么表单要有 `initialValues`？ | `initialValues` 是表单初始状态，不是替用户填写最终内容。受控表单的 `value` 来自 React state，所以页面刚打开时 state 需要一个初始值，例如事件描述为空、情绪强度默认 5、分析方向默认综合分析。提交成功后也可以用 `setValues(initialValues)` 快速重置表单。 | 阶段 3 | 已记录 |
| Props 类型里可以写函数吗？ | 可以。React props 可以传普通值，也可以传函数。`onSubmit: (values: ReflectionFormValues) => Promise<void>` 表示父组件传给表单一个异步提交函数；表单组件只收集数据并调用它，不直接关心保存逻辑。`Promise<void>` 表示异步动作完成后不返回具体数据。 | 阶段 3 | 已记录 |
| `export function ReflectionForm({ isSubmitting, onSubmit }: ReflectionFormProps)` 怎么理解？ | 这是定义并导出一个 React 函数组件。括号里是函数入参，也就是 props 对象；`{ isSubmitting, onSubmit }` 是对象解构，等价于从 `props.isSubmitting` 和 `props.onSubmit` 取值；`: ReflectionFormProps` 是给 props 参数标注类型。 | 阶段 3 | 已记录 |
| React 函数组件是什么意思？ | React 组件通常写成函数，函数接收 props/state 等输入，返回一段 TSX 描述 UI。可以理解为 `UI = function(props, state)`。`.tsx` 文件不一定都必须导出函数，但包含页面/组件 UI 的 `.tsx` 文件通常会定义函数组件。以前 React 也常用 class component，现在主流写法是 function component + Hooks。 | 阶段 3 | 已记录 |
| `const [values, setValues] = useState<ReflectionFormValues>(initialValues)` 怎么理解？ | `useState` 创建 React 状态，`<ReflectionFormValues>` 指定状态类型，`initialValues` 是初始值。`useState` 返回数组：第一项 `values` 是当前表单状态，第二项 `setValues` 是更新状态的函数。调用 `setValues(...)` 后，React 会重新渲染组件。 | 阶段 3 | 已记录 |
| `setValues((current) => ...)` 里的 `current` 是什么？ | 这是 React state 的函数式更新写法。`current` 是 React 传入的当前最新状态，也就是最新的 `values`。当新状态依赖旧状态时，例如切换情绪标签需要基于旧的 `emotion_tags` 判断是否已选中，推荐使用函数式更新，因为 React 状态更新可能异步合并，外层闭包里的 `values` 不一定永远是最新值。 | 阶段 3 | 已记录 |
| 什么是 React 受控表单？ | 受控表单是指表单控件的值由 React state 控制。`value={values.event_text}` 负责显示 state，`onChange` 读取用户输入并调用 `setValues` 更新 state。好处是提交时能直接拿完整 `values`，可以实时校验、控制按钮 disabled、提交后重置表单，也方便字段联动。 | 阶段 3 | 已记录 |
| 为什么表单提交要 `event.preventDefault()`？ | 浏览器原生 form 提交默认会刷新页面并跳转。React 单页应用通常不希望刷新页面，而是自己用 JavaScript 调接口，所以在 `handleSubmit` 中调用 `event.preventDefault()` 阻止默认行为，再执行自定义保存逻辑。 | 阶段 3 | 已记录 |
| `onChange={(event) => setValues({ ...values, event_text: event.target.value })}` 是什么？ | 这是受控输入框的更新逻辑：用户输入触发 `onChange`，`event.target.value` 读取当前输入值，`{ ...values, event_text: event.target.value }` 创建一个新对象，保留原表单其他字段，只替换 `event_text`。React 状态不推荐直接修改原对象，应通过 `setValues` 设置新对象来触发重新渲染。 | 阶段 3 | 已记录 |
| TSX 属性什么时候要用 `{}`？ | 在 JSX/TSX 里，属性值如果是 JavaScript/TypeScript 表达式，就要用 `{}`，例如 `onSubmit={handleSubmit}`、`value={values.event_text}`、`disabled={isSubmitting}`、`onChange={(event) => setValues(...)}`。如果是固定字符串，可以直接用引号，例如 `placeholder="今天发生了什么？"`、`type="submit"`。判断规则：固定字符串用 `"..."`，变量/函数/表达式用 `{...}`。 | 阶段 3 | 已记录 |
| `<input min="1" max="10">` 里的数字是字符串吗？ | 是。JSX/TSX 中 `min="1"`、`max="10"` 是字符串属性，HTML DOM 属性本来就是以字符串形式传递，浏览器会根据 `input type="range"` 理解成数字范围。也可以写成 `min={1}`、`max={10}`。但无论哪种写法，`event.target.value` 读取到的通常都是字符串，所以当前项目用 `Number(event.target.value)` 转成 `number`，匹配 `emotion_intensity: number`。 | 阶段 3 | 已记录 |
| 为什么 `event.target.value as FocusArea` 要用 `as`？ | `event.target.value` 在 TypeScript 里默认是普通 `string`，但 `focus_area` 的类型是 `FocusArea`，只能是固定几个字符串之一。由于选项来自 `focusOptions: FocusArea[]`，开发者知道这个值是合法的 FocusArea，于是用 `as FocusArea` 做类型断言。`as` 不改变运行时的值，只是告诉 TypeScript 按某个类型看待它；只有在确定来源可靠时才应该使用。 | 阶段 3 | 已记录 |
| form 里的普通按钮为什么要写 `type="button"`？ | 在 HTML 表单里，`button` 默认可能按提交按钮处理。如果情绪标签按钮不写 `type="button"`，点击标签时可能误触发表单提交。只有真正提交表单的按钮才写 `type="submit"`；普通交互按钮应显式写 `type="button"`。 | 阶段 3 | 已记录 |
| `ReflectionForm.tsx` 里面用的是组件库吗？ | 当前没有使用 Ant Design、MUI、shadcn/ui 等组件库。表单、输入框、下拉框、按钮都是原生 HTML 元素，样式用 Tailwind CSS 手写。阶段 3 这样做是为了优先理解 React 表单和状态基础。 | 阶段 3 | 已记录 |
| TSX 内容里的 `{new Date(...).toLocaleString()}` 怎么理解？ | TSX 内容中的 `{}` 不是模板字符串，而是表示执行 JavaScript 表达式并把结果渲染到页面。后端的 `datetime` 通过 JSON 返回时会变成字符串，因为 JSON 没有 datetime 类型，只有 string、number、boolean、null、object、array 等基础类型。前端用 `new Date(record.created_at)` 把时间字符串转成 JavaScript `Date` 对象，再用 `.toLocaleString()` 按当前浏览器语言、地区和时区格式化成人能读的本地时间。 | 阶段 3 | 已记录 |
| Vue `{{}}`、TSX `{}` 和模板字符串有什么区别？ | Vue 模板里的 `{{ message }}` 主要用于文本插值；TSX/JSX 里的 `{message}` 表示在页面结构中执行 JavaScript 表达式，既可用于文本，也可用于属性、条件、循环和事件回调；模板字符串是 JavaScript 字符串语法，外层用反引号，例如 `` `/api/reflections/${id}` ``，用于在字符串内部插入变量或表达式。简单记：Vue `{{}}` 是模板文本插值，TSX `{}` 是页面结构里的 JS 表达式，`` `${}` `` 是字符串里的插值。 | 阶段 3 | 已记录 |
| 为什么历史记录时间显示不对？ | 后端用 `datetime.now(timezone.utc)` 生成 UTC 时间，但 SQLite 没有真正的“带时区 datetime 类型”，写入/读出时可能只剩普通时间字符串，例如 `2026-07-05T07:54:09`，没有 `Z` 或 `+00:00`。前端 `new Date("2026-07-05T07:54:09")` 会倾向于按本地时间解析，导致 UTC 时间没有正确转换成北京时间。解决方式：前端显示时先判断字符串是否带时区；如果没有时区标记，就补 `Z` 按 UTC 解析，再用 `toLocaleString("zh-CN", { timeZone: "Asia/Shanghai", hour12: false })` 固定显示中国本地时间。 | 阶段 3 | 已记录 |
| `hour12: false` 是什么意思？ | `toLocaleString` 的 `hour12: false` 表示使用 24 小时制显示时间，而不是上午/下午的 12 小时制。例如更倾向显示 `15:54:09`，而不是 `下午3:54:09`。 | 阶段 3 | 已记录 |
| `/(?:Z|[+-]\d{2}:\d{2})$/.test(createdAt)` 是什么意思？ | 这是用正则判断时间字符串末尾是否带时区标记。`/.../` 是正则字面量；`.test(createdAt)` 返回是否匹配；`(?:...)` 是非捕获分组；`|` 表示或者；`Z` 匹配 UTC 标记；`[+-]\d{2}:\d{2}` 匹配 `+08:00`、`+00:00`、`-05:00` 这种时区偏移；`$` 表示必须在字符串结尾。匹配成功说明时间字符串已经有时区标记，不需要补 `Z`。 | 阶段 3 | 已记录 |
| `cp .env.example .env` 是什么意思？ | `cp` 是复制文件命令，格式是 `cp 源文件 目标文件`。阶段 4 开始后端需要读取大模型 API Key 等环境变量，所以先把安全模板 `.env.example` 复制成本地真实配置文件 `.env`，再在 `.env` 中填写真实 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 等配置。`.env.example` 可以提交 GitHub，`.env` 包含私密信息，已被 `.gitignore` 忽略，不能提交。 | 阶段 4 | 已记录 |
| 为什么 API Key 只能放后端，不能放前端？ | 浏览器 DevTools 看不到后端代码，因为后端代码运行在服务器/本机后端进程里，不会发给浏览器；但用户能看到前端打包后的 JS/CSS、Sources、Network 请求、本地存储和 DOM。只要 API Key 写进前端代码或前端可访问环境变量，就可能在 Sources 或打包产物里被搜索到；如果前端直接请求大模型 API，Authorization 请求头也会在 Network 里暴露。正确架构是：前端请求自己的 FastAPI 后端，后端读取 `.env` 里的 API Key，再由后端请求大模型服务。 | 阶段 4 | 已记录 |
| 为什么用 `Settings` 类读取环境变量，而不是普通方法？ | 普通方法当然也能一次性读取多个环境变量；使用 `Settings(BaseSettings)` 的核心价值是把配置对象化、可缓存，并获得类型转换/校验和编辑器提示。`Settings()` 会生成配置对象，调用处可以用 `settings.llm_api_key` 这类属性；`get_settings()` 配合 `@lru_cache` 可以复用同一个配置对象；Pydantic 会按字段类型转换 `.env` 里的字符串，例如把 `"60"` 转成 `int`，后续也方便增加 URL、枚举、范围等校验。主要优点是类型支持和校验，其次是对象化和缓存。 | 阶段 4 | 已记录 |
| `class Settings(BaseSettings)` 里的括号是什么意思？ | 在 Python 类定义里，`class Child(Parent):` 的括号表示继承父类，不是给类传参。`class Settings(BaseSettings):` 表示 `Settings` 继承 `BaseSettings`，类似 JavaScript 的 `class Settings extends BaseSettings`。对象创建时的括号才是传参，例如 `Settings()` 或 `Settings(llm_model="deepseek-chat")`。普通类通常通过 `__init__(self, ...)` 接收创建对象时的参数；当前 `Settings` 没有手写 `__init__`，因为 `BaseSettings` 父类已经提供初始化逻辑，会根据字段定义、环境变量和传入参数生成配置对象。 | 阶段 4 | 已记录 |
| 为什么 `model_config` 不像 `llm_api_key` 一样写类型？ | `llm_api_key: str = Field(...)` 是普通配置字段，会从环境变量读取并成为 `settings.llm_api_key`。`model_config = SettingsConfigDict(extra="ignore")` 不是业务配置字段，而是 Pydantic v2 识别的特殊类配置属性，用来告诉 Pydantic 这个模型类本身如何工作，例如遇到额外环境变量时忽略。它不从 `.env` 读取，也不会作为普通字段使用，所以通常不写类型声明。 | 阶段 4 | 已记录 |
| Python 的 `@` 装饰器语法是什么？ | `@xxx` 放在函数上方，表示用 `xxx` 给下面这个函数附加额外能力，本质上类似 `func = xxx(func)`。不同装饰器功能不同：`@lru_cache` 给函数增加缓存能力，第一次执行后复用结果；`@router.post(...)` / `@router.get(...)` 把函数注册成 FastAPI HTTP 接口处理函数；`@asynccontextmanager` 把异步生成器函数包装成异步上下文管理器。可以统一理解为：装饰器不改函数内部代码，但改变或扩展函数的使用方式。 | 阶段 4 | 已记录 |
| Python 三个双引号 `"""..."""` 有哪些用法？ | 三个双引号本质是多行字符串语法。如果它放在模块、类、函数开头且不赋值，通常作为 docstring 文档字符串，用来说明代码用途，并可被 `help()` 等工具读取；如果赋值给变量，例如 `REPORT_STRUCTURE = """..."""`，它就是普通多行字符串值，会作为真实业务内容使用。f-string 不一定要三引号，`f"你好，{name}"` 是单行 f-string；`f"""...{value}..."""` 是多行 f-string。当前 `SYSTEM_PROMPT = f"""..."""` 是因为既需要插入变量，又是多行提示词。 | 阶段 4 | 已记录 |
| `SYSTEM_PROMPT` 和 user prompt 怎么分工？ | `SYSTEM_PROMPT` 放长期规则，负责定义模型角色、安全边界、禁止事项、语气和输出格式，例如不做诊断、不替代咨询、必须输出固定 Markdown 结构。user prompt 放本次具体任务和用户输入，例如事件描述、情绪标签、强度、自动想法、身体反应和分析方向。简单记：system 管“你是谁、边界是什么、格式怎么输出”，user 管“这次要处理什么内容”。 | 阶段 4 | 已记录 |
| `rstrip("/")` 是什么作用？ | Python 字符串的 `rstrip("/")` 会去掉字符串右侧连续出现的 `/`。当前 `_chat_completions_url(base_url)` 里用它处理 `LLM_BASE_URL`，避免用户把 base url 写成 `https://api.openai.com/v1/` 时拼出 `https://api.openai.com/v1//chat/completions` 这种双斜杠地址。 | 阶段 4 | 已记录 |
| Python 函数名前面加 `_` 是什么意思？ | 例如 `_chat_completions_url`。单下划线开头是 Python 社区约定，表示这是模块内部辅助函数，不建议外部模块直接调用。Python 不会强制禁止访问，它不像真正的 private，只是给开发者和编辑器一个“内部实现细节”的信号。 | 阶段 4 | 已记录 |
| 大模型参数 `temperature` 是什么？ | `temperature` 用来控制模型输出的随机性/发散程度。值越低，输出越稳定、保守、可重复；值越高，输出越发散、有创造性，但也更容易不稳定。当前设置 `0.4` 是为了让情绪复盘报告语气更克制、结构更稳定。心理自助类内容不适合太高随机性。 | 阶段 4 | 已记录 |
| Python 的 `async with` 是什么？ | `async with` 是异步上下文管理器语法，用来管理需要异步打开/关闭的资源。当前 `async with httpx.AsyncClient(...) as client:` 表示创建一个异步 HTTP 客户端，代码块内用它发请求，离开代码块时自动异步关闭连接资源。它类似普通 `with`，但支持 `await` 场景。 | 阶段 4 | 已记录 |
| `with Session`、`async with httpx.AsyncClient`、`with open` 分别管理什么？ | 它们都是上下文管理器，作用是保证资源用完后释放，但管理的资源不同。`with Session(engine) as session` 管数据库 ORM Session/数据库会话资源；`async with httpx.AsyncClient() as client` 管 HTTP 客户端资源，例如 HTTP 连接、连接池、网络 socket、HTTPS 相关资源；`with open(...) as file` 管文件句柄。`with` 用于同步资源管理，`async with` 用于异步资源管理，适合需要 `await` 的异步 IO 场景。 | 阶段 4 | 已记录 |
| 为什么模型调用失败时返回 `502 Bad Gateway`？ | `502 Bad Gateway` 常用于表示当前后端服务本身收到了请求，但它依赖的上游服务失败了。当前项目里，FastAPI 后端是网关/中间层，大模型 API 是上游服务；如果模型 API 返回 401/429/500、网络失败、超时或响应格式异常，后端把它转换成 502，表示“上游模型服务调用失败”。 | 阶段 4 | 已记录 |
| Python 的 `except` 类似 JavaScript 的 `catch` 吗？ | 可以这样理解。Python 用 `try/except` 捕获异常，类似 JavaScript 的 `try/catch`。例如 `except httpx.HTTPStatusError as exc:` 表示捕获 `HTTPStatusError`，并把异常对象命名为 `exc`，方便读取 `exc.response.status_code` 等信息。 | 阶段 4 | 已记录 |
| `Authorization: Bearer xxx` 是什么意思？ | `Bearer` 字面意思是持有者/携带者。在 HTTP 鉴权里，`Authorization: Bearer <token>` 表示当前请求携带一个 bearer token，服务端用这个 token 判断调用方是否有权限。大模型 API Key 常通过 `Authorization: Bearer {LLM_API_KEY}` 传给模型服务。 | 阶段 4 | 已记录 |
| `httpx` 里的 `json=request_body` 是什么？ | `json=` 表示把这个 Python 对象作为 HTTP 请求体发送。`httpx` 会自动把 Python dict/list 序列化成 JSON 字符串，并通常自动设置 JSON 请求头。当前代码仍显式写了 `Content-Type: application/json`，是为了让请求语义更清楚。 | 阶段 4 | 已记录 |
| `response.raise_for_status()` 是什么？ | 它会检查响应 HTTP 状态码。状态码是 2xx 时不做事；如果是 400、401、429、500 等错误状态码，会抛出 `httpx.HTTPStatusError`，让代码进入异常处理分支。 | 阶段 4 | 已记录 |
| `response.json()` 是把响应转成 Python 数据吗？ | 是。它把响应里的 JSON 文本解析成 Python 数据结构，例如 JSON object 变成 dict，JSON array 变成 list。模型响应解析后，代码才能用 `data["choices"][0]["message"]["content"]` 读取生成内容。 | 阶段 4 | 已记录 |
| `httpx.HTTPStatusError` 和 `httpx.HTTPError` 有什么区别？ | `HTTPStatusError` 是 `response.raise_for_status()` 遇到错误状态码时抛出的异常，例如 401、429、500；`HTTPError` 是更宽泛的 httpx HTTP 异常基类，覆盖连接失败、超时、DNS 错误、请求发送失败、响应读取失败等。捕获时应先写更具体的 `HTTPStatusError`，再写更宽泛的 `HTTPError`。 | 阶段 4 | 已记录 |
| `raise ... from exc` 是什么？ | `raise HTTPException(...) from exc` 表示抛出新的异常，同时保留原始异常 `exc` 作为原因。这样 traceback 能看到错误链：原始错误可能是 `HTTPStatusError`，转换后的对外错误是 FastAPI `HTTPException`。这有利于调试。 | 阶段 4 | 已记录 |
| OpenAI-compatible 响应里的 `choices[0].message.content` 是什么？ | Chat Completions 常见响应结构是 `{"choices": [{"message": {"role": "assistant", "content": "模型生成内容"}}]}`。所以 `data["choices"][0]["message"]["content"]` 的意思是：从 choices 数组取第一个结果，再取 message 对象里的 content 字段。阶段 4 只需要记住模型真正生成的文本通常在 `choices[0].message.content`。 | 阶段 4 | 已记录 |
| `except (KeyError, IndexError, TypeError) as exc` 为什么有括号？ | 这是 Python 一次捕获多个异常类型的语法，不是解构赋值。括号里是一个异常类型元组，表示发生 `KeyError`、`IndexError`、`TypeError` 任意一种都进入这个分支。当前用于处理模型响应格式异常：缺字段会 `KeyError`，数组为空会 `IndexError`，层级类型不对可能 `TypeError`。 | 阶段 4 | 已记录 |
| Python 的 tuple 元组是什么？ | tuple 是 Python 的有序数据结构，写法通常是圆括号，例如 `("焦虑", "委屈")`；list 用方括号，例如 `["焦虑", "委屈"]`。两者都能保存一组有顺序的数据，主要区别是 list 可以修改，tuple 通常不可修改，所以 tuple 常用于表示一组固定值。在 `except (KeyError, IndexError, TypeError) as exc` 中，括号里的就是异常类型 tuple，表示这几个异常任意一个都由同一个分支处理。 | 阶段 4 | 已记录 |
| 为什么要用 `HTTPException` 转换错误，而不是都返回 500？ | 500 表示后端内部未知错误，如果所有失败都变成 500，前端和开发者很难判断具体原因。阶段 4 里，缺少 `LLM_API_KEY` 返回 503，表示服务因配置缺失暂不可用；模型上游调用失败或响应格式异常返回 502，表示后端依赖的上游模型服务失败。用 `HTTPException` 把内部错误转换成更具体的 HTTP 响应，可以让前端提示更清晰，也让排查问题更快。 | 阶段 4 | 已记录 |
| `await` 是不是就是等这一步完成？ | 对当前请求/当前函数来说，是的：`ai_report = await generate_reflection_report(payload)` 必须等模型返回报告后，才会继续创建数据库记录。但对整个 FastAPI 服务来说，`await` 等网络 IO 时会把执行权让出去，事件循环可以先处理其他请求。简单记：`await` 对当前函数是等待下一步结果；对整个异步服务是挂起当前任务，不阻塞所有任务。 | 阶段 4 | 已记录 |
| 事件循环是什么？ | 事件循环可以理解成异步程序里的任务调度器。它负责管理多个异步任务：当某个任务执行到 `await` 需要等待网络/IO 结果时，事件循环会先把这个任务挂起，转去执行其他已经准备好的任务；等 IO 完成后，再恢复原任务，从 `await` 后面继续执行。FastAPI 的 async 代码和 JavaScript 的 `await fetch(...)` 都依赖类似的事件循环机制。简单记：事件循环负责在任务等待 IO 时切出去做别的事，等结果回来再切回来。 | 阶段 4 | 已记录 |
| Clash 为什么会导致 `httpx` 报 SOCKS 相关错误？ | Clash 通常会在系统或 WSL 终端里设置代理环境变量，例如 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY=socks5://...`。`httpx` 默认会读取这些环境变量并尝试走代理；如果代理是 SOCKS，但只安装了普通 `httpx`，就可能报 `Using SOCKS proxy, but the 'socksio' package is not installed.`。解决方式是把依赖改成 `httpx[socks]>=0.27.0` 并重新安装 requirements，让 `httpx` 额外安装 `socksio` 来支持 SOCKS 代理。可以用 `env | grep -i proxy` 检查当前终端是否存在代理环境变量。 | 阶段 4 | 已记录 |
| 为什么阶段 4 要返回上游模型错误摘要？ | 如果模型 API 返回 400/401/429/500 时，后端只返回 `LLM API request failed with status 400`，排查成本很高，无法快速判断是模型名不支持、鉴权失败、限流还是请求体不兼容。阶段 4 增加了安全的上游错误摘要：只截取响应正文前 500 字符，不输出请求头或 API Key。这样前端/开发者能看到可排查信息，同时避免泄露敏感凭据。 | 阶段 4 | 已记录 |
| 如何把项目从 `/mnt/c` 迁移到 WSL 原生目录？ | 使用 `rsync` 复制源码和 Git 仓库，同时排除依赖、构建缓存、虚拟环境和本地数据库。命令：`mkdir -p ~/projects && rsync -av --exclude 'frontend/node_modules' --exclude 'frontend/.next' --exclude 'backend/.venv' --exclude 'backend/*.db' --exclude '**/__pycache__' /mnt/c/yun_project/mind-intelligence-agent/ ~/projects/mind-intelligence-agent/`。`mkdir -p` 创建目标父目录；`&&` 表示前一个命令成功后再执行后一个；`rsync -av` 表示按目录结构同步并显示过程；`--exclude` 用来跳过可重建的生成物。迁移后应以 `/home/yunyun/projects/mind-intelligence-agent` 为准，避免 `/mnt/c` 下的文件监听、SQLite 写入和缓存问题。 | 阶段 4 | 已记录 |
| `useState("")` 为什么可以用空字符串？ | `useState` 需要一个初始值。页面首次渲染时还没有真正的 `session_id`，所以先用空字符串表示“尚未初始化”，后续在 `useEffect` 中调用 `setSessionId(nextSessionId)` 更新为真实值。 | 阶段 3 | 已记录 |
| `useState("")` 为什么不用显式类型声明？ | TypeScript 可以根据初始值推断类型。`useState("")` 的初始值是字符串，所以推断 `sessionId` 是 `string`。但如果初始值不能准确表达类型，就需要显式写，例如空数组 `useState<ReflectionListItem[]>([])`，因为 `[]` 本身推不出数组元素类型。 | 阶段 3 | 已记录 |
| `const [sessionId, setSessionId] = useState("")` 怎么理解？ | `useState` 返回一个固定结构的数组：第一项是当前状态值，第二项是更新状态的函数。变量名可以自定义，但 React 社区约定写成 `[xxx, setXxx]`，例如 `sessionId` 和 `setSessionId`。 | 阶段 3 | 已记录 |
| `useEffect` 是什么？ | `useEffect` 是 React Hook，用来处理组件渲染后需要执行的副作用，例如请求接口、读取 `localStorage`、设置定时器、订阅事件、修改 `document.title`。当前项目用它在页面首次渲染后获取/创建 session，并加载历史记录。 | 阶段 3 | 已记录 |
| React 组件渲染是什么意思？ | React 里的渲染通常指组件的 state 或 props 变化后，React 重新执行组件函数，计算新的 UI。不是浏览器页面上任何变化都会导致 React 渲染；例如滚动、鼠标移动本身不一定触发组件重新渲染，除非这些变化被写入 React state。 | 阶段 3 | 已记录 |
| `useEffect` 的回调可以直接写成 async 吗？ | 不推荐。`async` 函数一定返回 Promise，但 `useEffect` 期望回调返回 `undefined` 或一个 cleanup 清理函数。如果直接返回 Promise，React 不会把它当作正确的清理函数。常见写法是在 effect 内部调用异步函数，例如 `void loadRecords()` 或定义内部 `async function run()` 后再执行。 | 阶段 3 | 已记录 |
| `void loadRecords(nextSessionId)` 为什么写 `void`？ | `loadRecords` 是 async 函数，会返回 Promise。`useEffect` 的回调不能直接返回 Promise，而当前代码只是启动这个异步任务，不在 effect 回调里 await 它，所以写 `void` 表示主动忽略这个 Promise 返回值，避免 linter 提示未处理 Promise。 | 阶段 3 | 已记录 |
| `useEffect(..., [])` 里的空数组是什么意思？ | 第二个参数是依赖数组。空数组 `[]` 表示这个 effect 只在组件首次挂载后执行一次；不传依赖数组则每次渲染后都执行；写 `[sessionId]` 则表示首次执行，并在 `sessionId` 变化后重新执行。 | 阶段 3 | 已记录 |
| 函数参数 `nextSessionId = sessionId` 是什么意思？ | 这是函数参数默认值。如果调用 `loadRecords("abc")`，`nextSessionId` 是 `"abc"`；如果调用 `loadRecords()` 没传参数，就默认使用当前 state 里的 `sessionId`。TypeScript 可以根据默认值 `sessionId` 推断 `nextSessionId` 是 string，也可以显式写 `nextSessionId: string = sessionId`。 | 阶段 3 | 已记录 |
| `loadRecords` 为什么定义在 `Home` 组件内部且不 export？ | 它只服务当前页面，不需要给其他文件调用；而且它依赖 `Home` 内部的 state 和 setState，例如 `sessionId`、`setIsLoading`、`setError`、`setRecords`。如果放到组件外部，就拿不到这些状态，反而需要传很多参数。 | 阶段 3 | 已记录 |
| `nextSessionId` 和 `sessionId` 有什么区别？ | `sessionId` 是 React state，调用 `setSessionId(nextSessionId)` 后不会立刻改变当前函数作用域里的 `sessionId`，而是在下一次渲染中拿到新值。`nextSessionId` 是当前刚从 `getOrCreateSessionId()` 拿到的真实值，立即可用，所以页面首次加载历史记录时要传 `nextSessionId`。 | 阶段 3 | 已记录 |
| `setSessionId` 为什么是下一次渲染才拿到新值？ | 调用 `setSessionId(nextSessionId)` 会让 React 记录状态更新并调度组件重新渲染。它不会立刻修改当前函数作用域里的 `sessionId` 变量，所以紧跟着读取 `sessionId` 可能仍是旧值；但下一次组件函数重新执行时，`sessionId` 就会变成新值。不是等“碰巧渲染”，而是 setState 本身会安排重新渲染。 | 阶段 3 | 已记录 |
| 为什么 React 不在 `setState` 后立刻修改当前变量？ | React 会把 state 更新调度到后续渲染流程，而不是像普通变量赋值一样立刻改当前闭包里的值。这样可以保持当前函数执行的稳定性，并把同一轮同步代码中的多次状态更新批处理成较少的重新渲染。可以简单记：`setState` 不是立即改当前变量，而是通知 React 稍后用新值重新渲染组件。 | 阶段 3 | 已记录 |
| 为什么 `listReflections(nextSessionId)` 不直接用 `sessionId`？ | 页面首次加载时，`setSessionId(nextSessionId)` 后当前闭包里的 `sessionId` 可能仍是初始空字符串。如果马上用 `sessionId` 请求，可能传空值；使用 `nextSessionId` 可以确保第一次加载列表时使用刚获取到的真实 session。 | 阶段 3 | 已记录 |
| `nextSessionId` 为什么只能在 `useEffect` 里用？ | `nextSessionId` 是 `useEffect` 回调函数内部定义的局部变量，只在这个函数作用域里有效，`handleCreateReflection` 等外部函数访问不到它。所以需要调用 `setSessionId(nextSessionId)` 把它保存进 React state。职责上，`nextSessionId` 是当前 effect 同步流程里立即可用的局部变量；`sessionId` 是跨渲染、跨事件函数使用的组件状态。 | 阶段 3 | 已记录 |
| `page.tsx` 在阶段 3 里负责什么？ | `page.tsx` 是阶段 3 的页面容器组件/编排层，负责初始化 `session_id`、加载历史列表、处理创建记录、选择详情、删除记录、管理 loading/error/selectedRecord 状态，并把状态和回调函数通过 props 传给 `ReflectionForm`、`HistoryList`、`ReflectionDetail`。子组件主要负责展示和局部交互，不直接请求接口。 | 阶段 3 | 已记录 |
| `try` 里 `return` 了还会执行 `finally` 吗？ | 会。`finally` 的语义是不管 `try` 成功、`catch` 捕获、`return` 还是 `throw`，最后都要执行，常用于关闭 loading 状态或清理资源。但一般不要在 `finally` 里再写 `return` 或 `throw`，否则可能覆盖前面的结果。 | 阶段 3 | 已记录 |

### 后端

| 问题 | 当前理解 | 实践来源 | 状态 |
| --- | --- | --- | --- |
| FastAPI 如何组织路由、模型和数据库代码？ | 阶段 1 先用 `backend/app/main.py` 作为入口，后续接口变多后再拆分 routes、models、database。 | 阶段 1-2 | 进行中 |
| Python 里的 `"""..."""` 是注释吗？ | 三个双引号包起来的是字符串。放在模块、函数或类开头时，通常作为 docstring（文档字符串），用于说明这个模块/函数/类的用途。普通注释使用 `#`。 | 阶段 1 | 已记录 |
| `__init__.py` 是做什么的？ | `__init__.py` 用来标记当前目录是一个 Python package。本项目里 `backend/app/__init__.py` 表示 `app/` 是包，所以可以用 `app.main` 表示 `app` 包里的 `main.py` 模块。现代 Python 有 namespace package，但初学项目保留 `__init__.py` 更清晰、更兼容。 | 阶段 1 | 已记录 |
| `routers/__init__.py` 和 `routers/__pycache__` 有什么区别？ | `routers/__init__.py` 是源码文件，用来标记 `routers/` 是 Python package，支持 `from app.routers import reflections` 这类导入，应该提交；`routers/__pycache__/` 是 Python 运行/导入模块时自动生成的字节码缓存目录，不是源码，不需要看，也不提交。 | 阶段 2 | 已记录 |
| `app.add_middleware(...)` 是什么意思？ | `add_middleware` 不是项目里自定义的函数，而是 `FastAPI()` 创建出来的 app 对象自带的方法。middleware 是请求进入路由函数前、响应返回浏览器前经过的一层处理逻辑。本项目用 `CORSMiddleware` 处理跨域，允许 `http://localhost:3000` 的前端请求后端。 | 阶段 1 | 已记录 |
| Python 和 JavaScript 是面向对象还是面向过程？ | 两者都是多范式语言，都支持面向过程、面向对象和函数式写法。不能简单说 Python 是面向对象、JavaScript 是面向过程；实际项目中主要写法通常由框架决定，例如 React 常见函数式/声明式风格，FastAPI 里会看到 `app` 对象及其方法。 | 阶段 1 | 已记录 |
| FastAPI 里的 `@app.get("/health")` 是什么意思？ | 这是 Python 装饰器写法。装饰器可以在不改函数内部代码的情况下给函数附加能力。在 FastAPI 中，`@app.get("/health")` 表示把下面的函数注册成 `GET /health` 接口；当请求进来时，FastAPI 会执行这个函数。 | 阶段 1 | 已记录 |
| Python 的 `dict` 是数组吗？ | 不是。Python 的 `dict` 是键值对结构，更接近 JavaScript object；Python 的 `list` 才更接近 JavaScript array。`{"status": "ok"}` 是 Python 字典，不是数组。 | 阶段 1 | 已记录 |
| `dict[str, str]` 里的 `[]` 为什么不像 JS 数组？ | 这里的 `[]` 是 Python 类型标注里的泛型语法，不是数组字面量。`dict[str, str]` 表示返回值是一个字典，key 是 `str`，value 也是 `str`，类似 TypeScript 里的 `Record<string, string>`。 | 阶段 1 | 已记录 |
| 为什么后端要返回 JSON 响应？ | HTTP 接口不能直接传 Python 对象。FastAPI 内部可以返回 Python dict，但会自动序列化成 JSON，浏览器或前端再把 JSON 解析成 JavaScript object。数据流可以理解为：Python dict -> JSON text -> JavaScript object。 | 阶段 1 | 已记录 |
| 后端启动命令分别是什么意思？ | `python3 -m venv .venv` 创建项目专属 Python 虚拟环境；`source .venv/bin/activate` 激活虚拟环境，让当前终端优先使用 `.venv` 里的 Python 和 pip；`python -m pip install -r requirements.txt` 按依赖清单安装 FastAPI、uvicorn 等包；`uvicorn app.main:app --reload` 启动 `backend/app/main.py` 里的 FastAPI 应用，`--reload` 表示开发时改代码自动重启。 | 阶段 1 | 已记录 |
| Python 命令里的 `-m` 是什么意思？ | `-m` 表示把某个 Python 模块当成脚本运行，例如 `python3 -m venv .venv` 是用当前 Python 运行内置模块 `venv` 来创建虚拟环境。常见写法还有 `python -m pip`、`python -m pytest`。 | 阶段 1 | 已记录 |
| 为什么 Python 模块可以当成脚本运行？ | Python 模块本质上也是 `.py` 代码。执行 `python file.py` 是按文件路径运行；执行 `python -m module_name` 是按模块名在当前 Python 环境里查找并运行。很多可执行包内部有 `__main__.py`，例如 `pip/__main__.py`，所以 `python -m pip` 会执行当前环境里的 pip 模块入口。 | 阶段 1 | 已记录 |
| 为什么推荐 `python -m pip install`？ | 直接执行 `pip install` 时，`pip` 可能指向系统全局 Python、其他虚拟环境或 Anaconda 环境，导致依赖装错地方。`python -m pip install` 明确使用当前这个 `python` 对应的 pip；如果已激活 `.venv`，依赖就会安装进当前项目虚拟环境。 | 阶段 1 | 已记录 |
| 为什么先用 `python3`，激活后又用 `python`？ | 创建虚拟环境前还没有 `.venv`，所以 `python3 -m venv .venv` 使用的是本机已有的 Python 3。执行 `source .venv/bin/activate` 后，当前终端的 `PATH` 会优先指向 `.venv/bin`，此时 `python` 通常就是当前项目虚拟环境里的 Python。 | 阶段 1 | 已记录 |
| `pip install -r requirements.txt` 里的 `-r` 是什么？ | `-r` 表示从 requirement file 读取依赖清单。`python -m pip install -r requirements.txt` 的意思是用当前 Python 对应的 pip，按照 `requirements.txt` 里列出的包安装依赖。 | 阶段 1 | 已记录 |
| `uvicorn` 是干什么的？ | FastAPI 负责定义 API 应用，但它本身不直接监听端口。`uvicorn` 是 ASGI Server，负责监听本地端口、接收 HTTP 请求、把请求交给 FastAPI 应用处理，并把响应返回给客户端。`uvicorn app.main:app --reload` 表示启动 `backend/app/main.py` 里的 `app`，并在开发时自动重载。 | 阶段 1 | 已记录 |
| `sudo apt install python3.12-venv` 是什么意思？ | `sudo` 表示用管理员权限执行命令；`apt` 是 Ubuntu/Debian 的系统包管理器；`install` 表示安装系统软件包；`python3.12-venv` 是 Python 3.12 创建虚拟环境所需的系统包。它和 `pip install` 不同：`apt` 安装系统级软件包，`pip` 安装 Python 项目依赖。 | 阶段 1 | 已记录 |
| `__pycache__` 是什么？ | `__pycache__` 是 Python 运行时自动生成的缓存目录，里面放 `.py` 编译后的字节码文件，例如 `main.cpython-312.pyc`。它可以加快模块加载，但不是源码，不需要提交到 GitHub，已通过 `.gitignore` 忽略。删除它不影响项目，下次运行 Python 可能会重新生成。 | 阶段 1 | 已记录 |
| `.venv` 是什么？ | `.venv` 是当前后端项目的 Python 虚拟环境目录，里面包含项目自己的 Python、pip、激活脚本和通过 `requirements.txt` 安装的第三方包。它是本地生成环境，不提交 GitHub；删除后可以通过 `python3 -m venv .venv` 和 `python -m pip install -r requirements.txt` 重建。现阶段不需要深究 `.venv` 内部文件。 | 阶段 1 | 已记录 |
| ORM 工具是什么意思？ | ORM 是 Object-Relational Mapping，对象关系映射。它的作用是用 Python 类和对象来表达数据库表和记录，减少手写 SQL。例如用 `ReflectionRecord` 类表示 `reflection_records` 表，用 `select(ReflectionRecord)` 查询记录。阶段 2 使用 SQLModel 作为 ORM。 | 阶段 2 | 已记录 |
| `models.py` 是做什么的？ | `models.py` 用来定义数据库表结构的 Python 表达。本项目里 `ReflectionRecord(SQLModel, table=True)` 对应 SQLite 里的 `reflection_records` 表；类属性对应表字段；字段类型和 `Field(...)` 配置共同决定数据库字段规则。 | 阶段 2 | 已记录 |
| SQLModel 里的 `Field(...)` 是什么？ | 字段类型声明负责说明字段是什么类型，例如 `id: int | None`；`Field(...)` 负责给字段添加数据库/校验配置，例如 `primary_key=True` 表示主键，`index=True` 表示建索引，`nullable=False` 表示不能为空，`default` 或 `default_factory` 表示默认值规则。 | 阶段 2 | 已记录 |
| 建索引有什么作用？ | 索引可以理解成数据库为某个字段建立的目录。没有索引时，按 `session_id` 查询可能需要逐行扫描整张表；有索引时，数据库可以先查目录，快速定位相关记录。本项目经常按 `session_id` 查询历史记录，所以给 `session_id` 建索引。 | 阶段 2 | 已记录 |
| `default_factory` 和 `default` 有什么区别？ | `default=utc_now()` 会在类定义加载时立即调用一次函数，后续可能复用同一个默认值；`default_factory=utc_now` 传入的是函数本身，不带括号，表示每次创建新记录需要默认值时再调用函数。时间字段应使用 `default_factory`，避免多条记录拿到同一个启动时刻。 | 阶段 2 | 已记录 |
| UTC 是什么，中国时区怎么表示？ | UTC 是 Coordinated Universal Time，协调世界时，是全球统一时间基准，不是时间戳。`datetime.now(timezone.utc)` 返回带 UTC 时区信息的 datetime。中国大陆通常使用 UTC+8，也就是 Asia/Shanghai；如果要生成中国时区时间，可以使用 `datetime.now(ZoneInfo("Asia/Shanghai"))`。数据库里通常建议存 UTC，展示时再转本地时区。 | 阶段 2 | 已记录 |
| SQLite 的 `check_same_thread=False` 是为什么？ | SQLite 默认要求一个连接只能在创建它的线程中使用；FastAPI/uvicorn 处理同步接口时可能把请求放在线程池中执行，因此同一个数据库连接相关操作可能跨线程触发检查错误。`check_same_thread=False` 关闭 SQLite 的同线程检查，是 FastAPI + SQLite 的常见配置。它不表示可以随意共享状态，项目仍通过每次请求创建独立 Session 来管理数据库操作。 | 阶段 2 | 已记录 |
| `engine`、`connection`、`Session`、`thread` 是什么关系？ | `engine` 是应用级数据库入口/连接工厂；`connection` 是更底层、真正和 SQLite 文件通信的数据库连接；`Session` 是 ORM 层的一次数据库操作会话，业务代码通过 `session.add/exec/commit` 操作数据库，Session 内部会通过 engine 使用底层 connection；`thread` 是执行 Python 代码的线程，不是数据库对象。请求流程可理解为：某个 thread 执行接口函数 -> FastAPI 通过 `get_session()` 创建 `Session(engine)` -> 接口用 Session 操作数据库。 | 阶段 2 | 已记录 |
| `check_same_thread=False` 配的是 Session 吗？ | 不是。它是传给 SQLite 底层 connection 的配置，表示不强制要求连接只能在创建它的线程中使用。业务代码仍然不直接操作 connection，而是通过 SQLModel/SQLAlchemy 的 Session 操作数据库。 | 阶段 2 | 已记录 |
| `with Session(engine) as session` 是什么语法？ | `with ... as ...` 是 Python 上下文管理器语法，用来管理需要打开/关闭的资源。`with Session(engine) as session` 表示创建一个数据库 Session，并在离开 `with` 代码块时自动关闭它，类似 `with open(...) as f` 会自动关闭文件。 | 阶段 2 | 已记录 |
| `yield session` 在 `get_session()` 里是什么意思？ | `yield session` 表示把数据库 session 暂时交给 FastAPI 接口使用。请求进来时 FastAPI 调用 `get_session()`，拿到 `yield` 出来的 session，接口用它查库/写库；接口执行结束后回到 `get_session()`，离开 `with` 代码块并自动关闭 session。 | 阶段 2 | 已记录 |
| `def get_session() -> Generator[Session, None, None]` 怎么理解？ | `def get_session()` 定义无参数函数；`->` 是返回类型标注；因为函数内部用了 `yield`，所以它返回生成器。`Generator[Session, None, None]` 三个参数分别表示：yield 出去的是 `Session`；不接收外部 send 进来的值；最终没有特殊 return 值。阶段 2 可简化理解为：这个函数会 yield 一个数据库 Session 给 FastAPI 使用。 | 阶段 2 | 已记录 |
| `models.py` 和 `schemas.py` 有什么区别？ | `models.py` 面向数据库，定义真实表结构，例如 `ReflectionRecord(SQLModel, table=True)` 会映射成 SQLite 表；`schemas.py` 面向 API，定义请求体和响应体结构，例如创建记录时前端要传什么字段、接口返回什么字段。简单记：models 关心怎么存，schemas 关心怎么收和怎么返。 | 阶段 2 | 已记录 |
| `class ReflectionCreate(SQLModel):` 是什么？ | 这是定义一个继承自 `SQLModel` 的普通数据模型，用于请求体验证、类型检查和接口文档生成。因为它没有 `table=True`，所以不会创建数据库表。FastAPI 会用它解析和校验创建记录接口的 JSON 请求体。 | 阶段 2 | 已记录 |
| `table=True` 和没有 `table=True` 有什么区别？ | `class ReflectionRecord(SQLModel, table=True)` 表示数据库表模型，会参与建表；`class ReflectionCreate(SQLModel)` 没有 `table=True`，只是普通数据结构，用于 API schema，不会建表。 | 阶段 2 | 已记录 |
| `Literal["helpful", "not_helpful"]` 是什么？ | `Literal` 是 Python 类型标注工具，用来限制字段只能取固定字面量值。本项目里 `feedback: Literal["helpful", "not_helpful"]` 表示反馈只能是 `helpful` 或 `not_helpful`，传其他值会校验失败。它类似 TypeScript 的 `"helpful" | "not_helpful"`。 | 阶段 2 | 已记录 |
| Python 的 `list[str]` 是数组吗？ | Python 的 `list` 基本对应 JavaScript 的 array。`emotion_tags: list[str]` 表示字符串列表，对应 JSON 里的 `["焦虑", "委屈"]`，类似 TypeScript 的 `string[]`。 | 阶段 2 | 已记录 |
| FastAPI 的 `/docs` 是怎么生成的？ | `/docs` 是 FastAPI 自动生成的 Swagger UI 接口文档。它不是只根据 `schemas.py` 生成，而是综合路由定义、HTTP 方法、路径、查询参数、请求体 schema、响应体 schema、类型标注和 `Field(...)` 校验规则生成。开发时可以直接在 `/docs` 页面测试接口。 | 阶段 2 | 已记录 |
| `reflections.py` 是做什么的？ | `reflections.py` 是阶段 2 的复盘记录路由文件，负责注册 `/api/reflections` 相关接口，并把 schema 校验、数据库 Session、ReflectionRecord 模型和 CRUD 操作串起来。它是阶段 2 API 读写 SQLite 的核心文件。 | 阶段 2 | 已记录 |
| `APIRouter` 是什么？ | `APIRouter` 用来把一组相关接口模块化管理，避免所有接口都写在 `main.py`。它不是 Next/Nuxt 那种目录结构自动生成路由；FastAPI 需要在代码里显式创建 `APIRouter(prefix=...)`、用 `@router.get/post` 注册接口，并在 `main.py` 中 `app.include_router(...)` 挂载后才生效。 | 阶段 2 | 已记录 |
| `main.py` 在后端里负责什么？ | `main.py` 是 FastAPI 后端应用总入口，负责创建 `app = FastAPI(...)`，配置应用生命周期 lifespan，启动时初始化数据库表，配置 CORS，注册 `/health` 健康检查接口，并通过 `app.include_router(reflections.router)` 挂载业务路由。 | 阶段 2 | 已记录 |
| `@asynccontextmanager` 是什么？ | `@asynccontextmanager` 是 Python 的装饰器，可以把一个异步生成器函数转换成异步上下文管理器。FastAPI 的 lifespan 使用这种形式描述应用启动前做什么、应用关闭时做什么。 | 阶段 2 | 已记录 |
| 为什么 `lifespan` 要写成 `async def`？ | FastAPI/ASGI 的应用生命周期支持异步初始化和清理，例如以后可能需要 `await` 连接远程服务或关闭客户端。当前 `create_db_and_tables()` 是同步逻辑，但使用 `async def lifespan(...)` 符合 FastAPI 推荐的 lifespan 写法。 | 阶段 2 | 已记录 |
| `lifespan(app: FastAPI)` 里的 `app` 为什么当前没用也要传？ | 这是 FastAPI lifespan 的函数签名约定，框架会调用 `lifespan(app)` 并传入当前 FastAPI 应用对象。当前阶段只初始化数据库表，所以没用到 `app`；以后可以用 `app.state` 存应用级资源，例如模型客户端、缓存、配置对象等。 | 阶段 2 | 已记录 |
| `AsyncGenerator[None, None]` 是什么？ | 因为 `lifespan` 是 `async def` 且内部使用 `yield`，所以它是异步生成器。`AsyncGenerator[None, None]` 表示这个异步生成器 yield 出去的值是 `None`，也不接收外部 send 进来的值。当前 lifespan 的 `yield` 只是用来分隔启动阶段和运行/关闭阶段。 | 阶段 2 | 已记录 |
| `lifespan` 里的 `yield` 和 `get_session` 里的 `yield` 有什么区别？ | 两者都用来把函数分成“前置逻辑”和“后置清理”两段。`get_session` 里 `yield session` 是把数据库 Session 交给接口使用，用完后退出 `with` 自动关闭；`lifespan` 里 `yield` 是启动逻辑和关闭逻辑的分界线，`yield` 前执行应用启动初始化，`yield` 后可写应用关闭清理逻辑。 | 阶段 2 | 已记录 |
| 编辑器提示 `import fastapi could not be resolved` 是什么？ | 这通常是 VS Code/Pylance 没选中后端虚拟环境解释器导致的类型提示问题，不一定是运行错误。应选择 `backend/.venv/bin/python` 作为 Python interpreter；只要后端能启动，说明运行环境里有 fastapi。 | 阶段 2 | 已记录 |
| Python f-string 是什么？ | `f"{text[:max_length]}..."` 是 Python 格式化字符串，前缀 `f` 表示可以在字符串里用 `{}` 插入表达式结果。`text[:max_length]` 表示截取前 `max_length` 个字符，所以结果类似 `"abc..."`。 | 阶段 2 | 已记录 |
| `record_id` 和 `session_id` 为什么要同时满足？ | `record_id` 标识某一条记录，`session_id` 标识这条记录属于哪个匿名用户/会话。查询详情、删除、反馈时必须同时满足 `id == record_id` 且 `session_id == 当前用户`，否则用户可能通过改 URL 里的 ID 访问或修改别人数据。 | 阶段 2 | 已记录 |
| `session.exec(statement).first()` 是什么意思？ | `session.exec(statement)` 表示用当前数据库 Session 执行 SQLModel 查询语句；`.first()` 表示只取第一条结果，如果没有结果则返回 `None`。按主键 ID 查询理论上最多只有一条，所以适合用 `first()`。 | 阶段 2 | 已记录 |
| `Depends(get_session)` 是什么意思？ | `Depends` 是 FastAPI 依赖注入。`session: Session = Depends(get_session)` 表示这个接口需要数据库 Session，FastAPI 会自动调用 `get_session()`，把 yield 出来的 session 传给接口函数。 | 阶段 2 | 已记录 |
| `Query(..., min_length=1)` 是什么意思？ | `Query` 用来声明和校验 URL query 参数。`...` 在这里表示该参数必填；`min_length=1` 表示字符串最短长度为 1。因此 `session_id: str = Query(..., min_length=1)` 表示必须在 URL 中传 `?session_id=xxx`。 | 阶段 2 | 已记录 |
| 什么时候需要 `session.refresh(record)`？ | `refresh` 用来从数据库重新加载对象的最新状态。创建后常用它获取数据库生成的 `id`、默认值或时间字段；修改后如果要返回最新对象，也可以 refresh；删除后记录已不存在，不需要 refresh；单纯查询也不需要 refresh。 | 阶段 2 | 已记录 |
| `session.add(record)` 是新增还是追踪变化？ | 更准确地说，`session.add(record)` 是把对象加入当前 Session 的管理范围。新对象被 add 后，commit 会执行 INSERT；已存在对象如果已被 Session 查询出来，通常已经处于管理状态，修改字段后 commit 会执行 UPDATE，不一定需要再次 add。可以简化理解为：add 让 Session 管理对象，Session 管理的对象会在 commit 时把变化同步到数据库。 | 阶段 2 | 已记录 |
| payload 和 query 有什么区别？ | query 是 URL 上的查询参数，例如 `GET /api/reflections?session_id=demo-session`，适合筛选条件、分页、搜索关键词、简单标识；payload 通常指请求体 body 里的 JSON 数据，适合创建/修改数据、复杂结构、较长内容。 | 阶段 2 | 已记录 |
| path 参数、query 参数、payload 怎么区分？ | 出现在路径模板里的参数是 path 参数，例如 `@router.post("/{record_id}/feedback")` 里的 `{record_id}` 会自动对应函数参数 `record_id: int`；`?` 后面的参数是 query 参数，例如 `?session_id=demo-session`；请求体 JSON 是 payload/body，例如 `payload: FeedbackUpdate`。不一定要显式写 `Path(...)`，FastAPI 会根据路径模板自动识别 path 参数。 | 阶段 2 | 已记录 |
| 什么时候用 query，什么时候用 payload？ | 一般查询类 GET 接口常用 query，例如列表接口按 `session_id` 筛选；创建或修改类 POST/PUT/PATCH 接口常用 payload，例如创建复盘记录或提交反馈。具体还要结合接口语义和数据复杂度。 | 阶段 2 | 已记录 |
| 为什么 POST 创建接口写 `status_code=201`，GET 列表接口没写？ | FastAPI 成功响应默认是 `200 OK`。GET 查询成功用默认 200 很合适，所以可以不写；POST 创建资源更标准的状态码是 `201 Created`，所以创建记录接口显式写 `status_code=status.HTTP_201_CREATED`。DELETE 如果返回 `{"deleted": true}`，也可以使用默认 200。 | 阶段 2 | 已记录 |
| `session.commit()` 是做什么的？ | `commit()` 是把当前 Session 中累计的数据库变化真正提交到数据库。新增对象、修改字段、删除对象在 commit 前还只是当前数据库事务里的变化；执行 commit 后才会持久化到 SQLite 文件。简单链路：`add/delete/修改字段` 表示 Session 里有变化，`commit` 表示把变化落库，`refresh` 表示从数据库重新读取最新对象。 | 阶段 2 | 已记录 |
| `session.add/commit` 可以类比 Git 的 `add/commit` 吗？ | 可以作为初步类比：`git add` 把文件变化加入暂存区，`session.add` 把对象加入 Session 管理；`git commit` 把暂存变化提交到 Git 仓库，`session.commit` 把 Session 中的数据库变化提交到数据库。但两者不完全一样：Git 管代码版本历史，数据库 Session 管对象状态；数据库 commit 更准确是提交事务。 | 阶段 2 | 已记录 |

### 数据库

| 问题 | 当前理解 | 实践来源 | 状态 |
| --- | --- | --- | --- |
| SQLite 在 MVP 中适合承担什么角色？ | 待补充 | 阶段 2 | 未开始 |

## LLM 应用基础

| 问题 | 当前理解 | 实践来源 | 状态 |
| --- | --- | --- | --- |
| Prompt Engineering 在产品里具体负责什么？ | 待补充 | 阶段 4 | 未开始 |
| 为什么 API Key 只能放在后端？ | 待补充 | 阶段 4 | 未开始 |
| 非流式响应和流式响应的工程差异是什么？ | 待补充 | 阶段 4-5 | 未开始 |

## RAG

| 问题 | 当前理解 | 实践来源 | 状态 |
| --- | --- | --- | --- |
| RAG 解决的核心问题是什么？ | 当前项目第一版暂不做 RAG，后续作为进阶主题学习。 | 路线图阶段 3 | 暂缓 |

## Agent 与工作流

| 问题 | 当前理解 | 实践来源 | 状态 |
| --- | --- | --- | --- |
| Agent 和普通 LLM 调用的区别是什么？ | 当前项目第一版暂不做 Agent，先完成 AI 产品闭环。 | 路线图阶段 4 | 暂缓 |
| Tool Calling 在什么场景下有必要？ | 待补充 | 后续 Agent 项目 | 未开始 |

## 生产化与运维

| 问题 | 当前理解 | 实践来源 | 状态 |
| --- | --- | --- | --- |
| 一个 AI Demo 到可上线系统之间差什么？ | 待补充 | 阶段 6 | 未开始 |
| 日志、错误处理、限流、成本控制分别解决什么问题？ | 待补充 | 阶段 5-6 | 未开始 |

## 项目实践记录

### AI 情绪复盘助手

| 阶段 | 目标 | 关键产出 | 状态 |
| --- | --- | --- | --- |
| 阶段 1 | 项目骨架 | 前端 Next.js、后端 FastAPI、健康检查、README | 进行中 |
| 阶段 2 | SQLite 数据库 | reflection_records 表和 CRUD 接口 | 进行中 |
| 阶段 3 | 前端表单和历史记录 | 表单、session_id、列表、详情、删除 | 进行中 |
| 阶段 4 | 接入大模型 API | 后端模型调用、Markdown 报告、保存记录 | 进行中 |
| 阶段 5 | 流式输出 | 后端流式响应、前端逐步展示、异常状态 | 未开始 |
| 阶段 6 | 体验完善 | Markdown 渲染、校验、错误处理、隐私提示 | 未开始 |

## 阶段复盘

### 阶段 0：项目准备

- 日期：2026-06-29
- 已完成：初始化 Git 仓库，绑定 GitHub，整理学习资料和项目 PRD。
- 当前判断：先做 AI 全栈闭环，再进入 RAG 和 Agent。
- 下一步：开始阶段 1 项目骨架。

### 阶段 1：项目骨架

- 日期：2026-06-29
- 已完成：创建 `frontend/` 和 `backend/` 目录，前端使用 Next.js，后端使用 FastAPI，并提供 `/health` 健康检查接口。
- 当前理解：前端负责页面和交互，后端负责 API、数据、模型调用和密钥保护；两者本地开发时分别启动。
- 验证结果：前端依赖安装成功，`npm run build` 通过；后端 `main.py` 语法检查通过。
- 待验证：后端实际启动还未完成，因为系统缺少 `python3.12-venv/ensurepip`，创建虚拟环境会失败。

### 阶段 2：SQLite 数据库

- 日期：2026-07-01
- 已完成：接入 SQLite 和 SQLModel，创建 `reflection_records` 表模型，拆分 `database.py`、`models.py`、`schemas.py`、`routers/reflections.py`。
- 已实现：创建测试记录、查询列表、查询详情、提交反馈、删除记录，并通过 `session_id` 做数据隔离。
- 验证结果：`/health` 正常；创建记录、列表、详情、错误 session 隔离、反馈、删除、删除后列表为空均已通过接口验证。
- 当前理解：阶段 2 的重点是让后端从“只返回健康检查”升级为“能通过 API 读写 SQLite 数据”。
- 卡点记录：接口验证时曾出现后端返回 500。原因是后端服务仍运行着旧代码/旧 schema 状态，虽然 FastAPI 开发模式有 `--reload`，但并不是所有运行态问题都能靠热更新自动恢复。处理方式是停止后端服务后重新启动，再刷新 `/docs` 重新测试接口。

### 阶段 3：前端表单和历史记录

- 日期：2026-07-03
- 已完成：新增前端表单、历史记录列表、历史详情、API 封装、匿名 `session_id` 管理和前端类型定义。
- 已实现：表单提交创建记录、列表加载、详情查询、删除记录，并通过 `localStorage` 保存匿名 `session_id`。
- 验证结果：`npm run build` 通过；后端 CRUD 请求结构验证通过。
- 当前理解：阶段 3 的重点是让前端状态、表单输入和后端 CRUD 接口连起来。
- 卡点记录：打开前端页面时出现 Next.js Runtime Error：`Cannot find module './833.js'`。排查发现当前终端 Node 版本是 `v16.20.2`，而项目要求 Node 20，且 `.next` 编译缓存可能不一致。处理方式：停止前端 dev server，执行 `nvm use 20` 确认 `node -v` 为 20，再删除 `frontend/.next` 并重新执行 `npm run dev`。经验：热更新适合普通源码改动，但依赖变化、Node 版本变化、`.next` chunk 缺失、manifest 不一致等问题应重启服务并清理生成缓存。
- 卡点记录：前端提交复盘记录时后端返回 500，后端日志为 `sqlite3.OperationalError: attempt to write a readonly database`。原因是 SQLite 配置 `sqlite:///./reflection_records.db` 使用相对路径，实际数据库位置取决于启动 `uvicorn` 时所在目录；旧后端进程可能连接了旧启动目录下的只读/异常数据库。处理方式：停止后端服务，固定从 `backend/` 目录重新启动，确认 `reflection_records.db` 生成在 `backend/` 下后重新测试成功。经验：重启经常能解决运行态、旧连接、启动目录、热更新残留问题，但要同时理解根因，避免把所有问题都当成“玄学重启”。

### 阶段 4：接入大模型 API

- 日期：2026-07-05
- 已完成：新增后端大模型配置读取、Prompt 管理、OpenAI-compatible 非流式模型调用，并把创建复盘记录流程改为“生成 AI 报告后保存 SQLite”。
- 当前实现：前端不再提交测试 `ai_report`，只提交用户输入和 `session_id`；后端负责调用大模型生成 Markdown 报告。
- 当前理解：API Key 必须只放在后端 `.env`，前端只能请求自己的后端接口，不能直接调用模型服务。
- 待验证：需要配置真实 `LLM_API_KEY` 后，从前端提交表单验证 AI 报告生成和保存。

## 待解决问题

| 问题 | 分类 | 优先级 | 触发场景 | 处理状态 |
| --- | --- | --- | --- | --- |
| Next.js 前端和 FastAPI 后端在本地开发时如何组织目录和启动？ | 基础全栈工程能力 | 高 | 阶段 1 | 进行中 |
| 前后端分离项目的 README 应该写哪些内容才适合简历展示？ | 生产化与工程表达 | 中 | 阶段 1 | 待解决 |
