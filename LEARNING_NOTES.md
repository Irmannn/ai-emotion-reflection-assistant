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
| 阶段 3 | 前端表单和历史记录 | 表单、session_id、列表、详情、删除 | 未开始 |
| 阶段 4 | 接入大模型 API | 后端模型调用、Markdown 报告、保存记录 | 未开始 |
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

## 待解决问题

| 问题 | 分类 | 优先级 | 触发场景 | 处理状态 |
| --- | --- | --- | --- | --- |
| Next.js 前端和 FastAPI 后端在本地开发时如何组织目录和启动？ | 基础全栈工程能力 | 高 | 阶段 1 | 进行中 |
| 前后端分离项目的 README 应该写哪些内容才适合简历展示？ | 生产化与工程表达 | 中 | 阶段 1 | 待解决 |
